# Scrapy教程06- Item Pipeline

当一个item被蜘蛛爬取到之后会被发送给Item Pipeline，然后多个组件按照顺序处理这个item。
每个Item Pipeline组件其实就是一个实现了一个简单方法的Python类。他们接受一个item并在上面执行逻辑，还能决定这个item到底是否还要继续往下传输，如果不要了就直接丢弃。

使用Item Pipeline的常用场景：

* 清理HTML数据
* 验证被抓取的数据(检查item是否包含某些字段)
* 重复性检查(然后丢弃)
* 将抓取的数据存储到数据库中

## 编写自己的Pipeline
定义一个Python类，然后实现方法`process_item(self, item, spider)`即可，返回一个字典或Item，或者抛出`DropItem`异常丢弃这个Item。

或者还可以实现下面几个方法：

* `open_spider(self, spider)` 蜘蛛打开的时执行
* `close_spider(self, spider)` 蜘蛛关闭时执行
* `from_crawler(cls, crawler)` 可访问核心组件比如配置和信号，并注册钩子函数到Scrapy中

## Item Pipeline示例

### 价格验证
我们通过一个价格验证例子来看看怎样使用
``` python
from scrapy.exceptions import DropItem

class PricePipeline(object):

    vat_factor = 1.15

    def process_item(self, item, spider):
        if item['price']:
            if item['price_excludes_vat']:
                item['price'] = item['price'] * self.vat_factor
            return item
        else:
            raise DropItem("Missing price in %s" % item)
```

### 将item写入json文件
下面的这个Pipeline将所有的item写入到一个单独的json文件，一行一个item
``` python
import json

class JsonWriterPipeline(object):

    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
```

### 将item存储到MongoDB中
这个例子使用[pymongo](http://api.mongodb.org/python/current/)来演示怎样讲item保存到MongoDB中。
MongoDB的地址和数据库名在配置中指定，这个例子主要是向你展示怎样使用`from_crawler()`方法，以及如何清理资源。
``` python
import pymongo

class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        return item
```

### 重复过滤器
假设我们的item里面的id字典是唯一的，但是我们的蜘蛛返回了多个相同id的item
``` python
from scrapy.exceptions import DropItem

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item
```

## 激活一个Item Pipeline组件
你必须在配置文件中将你需要激活的Pipline组件添加到`ITEM_PIPELINES`中
``` python
ITEM_PIPELINES = {
    'myproject.pipelines.PricePipeline': 300,
    'myproject.pipelines.JsonWriterPipeline': 800,
}
```
后面的数字表示它的执行顺序，从低到高执行，范围0-1000

## Feed exports
这里顺便提下Feed exports，一般有的爬虫直接将爬取结果序列化到文件中，并保存到某个存储介质中。只需要在settings里面设置几个即可：
```
* FEED_FORMAT= json # json|jsonlines|csv|xml|pickle|marshal
* FEED_URI= file:///tmp/export.csv|ftp://user:pass@ftp.example.com/path/to/export.csv|s3://aws_key:aws_secret@mybucket/path/to/export.csv|stdout:
* FEED_EXPORT_FIELDS = ["foo", "bar", "baz"] # 这个在导出csv的时候有用
```

## 请求和响应
Scrapy使用`Request`和`Response`对象来爬取网站。`Request`对象被蜘蛛生成，然后被传递给下载器，之后下载器处理这个`Request`后返回`Response`对象，然后返回给生成`Request`的这个蜘蛛。

### 给回调函数传递额外的参数
`Request`对象生成的时候会通过关键字参数`callback`指定回调函数，`Response`对象被当做第一个参数传入，有时候我们想传递额外的参数，比如我们构建某个Item的时候，需要两步，第一步是链接属性，第二步是详情属性，可以指定`Request.meta`
``` python
def parse_page1(self, response):
    item = MyItem()
    item['main_url'] = response.url
    request = scrapy.Request("http://www.example.com/some_page.html",
                             callback=self.parse_page2)
    request.meta['item'] = item
    return request

def parse_page2(self, response):
    item = response.meta['item']
    item['other_url'] = response.url
    return item

```

### Request子类
Scrapy为各种不同的场景内置了很多Request子类，你还可以继承它自定义自己的请求类。

`FormRequest`这个专门为form表单设计，模拟表单提交的示例
``` python
return [FormRequest(url="http://www.example.com/post/action",
                    formdata={'name': 'John Doe', 'age': '27'},
                    callback=self.after_post)]
```

我们再来一个例子模拟用户登录，使用了`FormRequest.from_response()`
``` python
import scrapy

class LoginSpider(scrapy.Spider):
    name = 'example.com'
    start_urls = ['http://www.example.com/users/login.php']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'username': 'john', 'password': 'secret'},
            callback=self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if "authentication failed" in response.body:
            self.logger.error("Login failed")
            return

        # continue scraping with authenticated session...
```

### Response子类
一个`scrapy.http.Response`对象代表了一个HTTP相应，通常是被下载器下载后得到，并交给Spider做进一步的处理。Response也有很多默认的子类，用于表示各种不同的响应类型。

* TextResponse 在基本`Response`类基础之上增加了编码功能，专门用于二进制数据比如图片、声音或其他媒体文件
* HtmlResponse 此类是`TextResponse`的子类，通过查询HTML的`meta http-equiv `属性实现了编码自动发现
* XmlResponse  此类是`TextResponse`的子类，通过查询XML声明实现编码自动发现

