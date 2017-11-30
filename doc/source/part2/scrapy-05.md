# Scrapy教程05- Item详解

Item是保存结构数据的地方，Scrapy可以将解析结果以字典形式返回，但是Python中字典缺少结构，在大型爬虫系统中很不方便。

Item提供了类字典的API，并且可以很方便的声明字段，很多Scrapy组件可以利用Item的其他信息。

## 定义Item
定义Item非常简单，只需要继承`scrapy.Item`类，并将所有字段都定义为`scrapy.Field`类型即可
``` python
import scrapy

class Product(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)
```
## Item Fields
`Field`对象可用来对每个字段指定元数据。例如上面`last_updated`的序列化函数指定为`str`，可任意指定元数据，不过每种元数据对于不同的组件意义不一样。

## Item使用示例
你会看到Item的使用跟Python中的字典API非常类似
### 创建Item
``` python
>>> product = Product(name='Desktop PC', price=1000)
>>> print product
Product(name='Desktop PC', price=1000)
```
### 获取值
``` python
>>> product['name']
Desktop PC
>>> product.get('name')
Desktop PC

>>> product['price']
1000

>>> product['last_updated']
Traceback (most recent call last):
    ...
KeyError: 'last_updated'

>>> product.get('last_updated', 'not set')
not set

>>> product['lala'] # getting unknown field
Traceback (most recent call last):
    ...
KeyError: 'lala'

>>> product.get('lala', 'unknown field')
'unknown field'

>>> 'name' in product  # is name field populated?
True

>>> 'last_updated' in product  # is last_updated populated?
False

>>> 'last_updated' in product.fields  # is last_updated a declared field?
True

>>> 'lala' in product.fields  # is lala a declared field?
False
```

### 设置值
``` python
>>> product['last_updated'] = 'today'
>>> product['last_updated']
today

>>> product['lala'] = 'test' # setting unknown field
Traceback (most recent call last):
    ...
KeyError: 'Product does not support field: lala'
```

### 访问所有的值
``` python
>>> product.keys()
['price', 'name']

>>> product.items()
[('price', 1000), ('name', 'Desktop PC')]
```

## Item Loader
Item Loader为我们提供了生成Item的相当便利的方法。Item为抓取的数据提供了容器，而Item Loader可以让我们非常方便的将输入填充到容器中。

下面我们通过一个例子来展示一般使用方法：
``` python
from scrapy.loader import ItemLoader
from myproject.items import Product

def parse(self, response):
    l = ItemLoader(item=Product(), response=response)
    l.add_xpath('name', '//div[@class="product_name"]')
    l.add_xpath('name', '//div[@class="product_title"]')
    l.add_xpath('price', '//p[@id="price"]')
    l.add_css('stock', 'p#stock]')
    l.add_value('last_updated', 'today') # you can also use literal values
    return l.load_item()
```
注意上面的`name`字段是从两个xpath路径添累加后得到。

## 输入/输出处理器
每个Item Loader对每个`Field`都有一个输入处理器和一个输出处理器。输入处理器在数据被接受到时执行，当数据收集完后调用`ItemLoader.load_item() `时再执行输出处理器，返回最终结果。
``` python
l = ItemLoader(Product(), some_selector)
l.add_xpath('name', xpath1) # (1)
l.add_xpath('name', xpath2) # (2)
l.add_css('name', css) # (3)
l.add_value('name', 'test') # (4)
return l.load_item() # (5)
```
执行流程是这样的：

1. `xpath1`中的数据被提取出来，然后传输到`name`字段的输入处理器中，在输入处理器处理完后生成结果放在Item Loader里面(这时候没有赋值给item)
2. `xpath2`数据被提取出来，然后传输给(1)中同样的输入处理器，因为它们都是`name`字段的处理器，然后处理结果被附加到(1)的结果后面
3. 跟2一样
4. 跟3一样，不过这次是直接的字面字符串值，先转换成一个单元素的可迭代对象再传给输入处理器
5. 上面4步的数据被传输给`name`的输出处理器，将最终的结果赋值给`name`字段

## 自定义Item Loader
使用类定义语法，下面是一个例子
``` python
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join

class ProductLoader(ItemLoader):

    default_output_processor = TakeFirst()

    name_in = MapCompose(unicode.title)
    name_out = Join()

    price_in = MapCompose(unicode.strip)

    # ...
```
通过`_in`和`_out`后缀来定义输入和输出处理器，并且还可以定义默认的`ItemLoader.default_input_processor`和`ItemLoader.default_input_processor`.

## 在Field定义中声明输入/输出处理器
还有个地方可以非常方便的添加输入/输出处理器，那就是直接在Field定义中
``` python
import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

def filter_price(value):
    if value.isdigit():
        return value

class Product(scrapy.Item):
    name = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_tags, filter_price),
        output_processor=TakeFirst(),
    )
```
优先级：

1. 在Item Loader中定义的`field_in`和`field_out`
1. Filed元数据(`input_processor`和`output_processor`关键字)
1. Item Loader中的默认的

Tips：一般来讲，将输入处理器定义在Item Loader的定义中`field_in`，然后将输出处理器定义在Field元数据中

## Item Loader上下文
Item Loader上下文被所有输入/输出处理器共享，比如你有一个解析长度的函数
``` python
def parse_length(text, loader_context):
    unit = loader_context.get('unit', 'm')
    # ... length parsing code goes here ...
    return parsed_length
```

初始化和修改上下文的值
``` python
loader = ItemLoader(product)
loader.context['unit'] = 'cm'

loader = ItemLoader(product, unit='cm')

class ProductLoader(ItemLoader):
    length_out = MapCompose(parse_length, unit='cm')
```

## 内置的处理器

1. `Identity` 啥也不做
1. `TakeFirst` 返回第一个非空值，通常用作输出处理器
1. `Join` 将结果连起来，默认使用空格' '
1. `Compose` 将函数链接起来形成管道流，产生最后的输出
1. `MapCompose` 跟上面的`Compose`类似，区别在于内部结果在函数中的传递方式.
它的输入值是可迭代的，首先将第一个函数依次作用于所有值，产生新的可迭代输入，作为第二个函数的输入，最后生成的结果连起来返回最终值，一般用在输入处理器中。
1. `SelectJmes` 使用json路径来查询值并返回结果

