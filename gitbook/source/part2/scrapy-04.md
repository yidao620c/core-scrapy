# Scrapy教程04- Selector详解

在你爬取网页的时候，最普遍的事情就是在页面源码中提取需要的数据，我们有几个库可以帮你完成这个任务：

1. [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)是python中一个非常流行的抓取库,
它还能合理的处理错误格式的标签，但是有一个唯一缺点就是：它运行很慢。
2. [lxml](http://lxml.de/)是一个基于[ElementTree](https://docs.python.org/2/library/xml.etree.elementtree.html)的XML解析库(同时还能解析HTML),
不过lxml并不是Python标准库

而Scrapy实现了自己的数据提取机制，它们被称为选择器，通过[XPath](http://www.w3.org/TR/xpath)或[CSS](http://www.w3.org/TR/selectors)表达式在HTML文档中来选择特定的部分

[XPath](http://www.w3.org/TR/xpath)是一用来在XML中选择节点的语言，同时可以用在HTML上面。
[CSS](http://www.w3.org/TR/selectors)是一种HTML文档上面的样式语言。

Scrapy选择器构建在lxml基础之上，所以可以保证速度和准确性。

本章我们来详细讲解下选择器的工作原理，还有它们极其简单和相似的API，比lxml的API少多了，因为lxml可以用于很多其他领域。

完整的API请查看[Selector参考](http://doc.scrapy.org/en/latest/topics/selectors.html#topics-selectors-ref)

## 关于选择器
Scrapy帮我们下载完页面后，我们怎样在满是html标签的内容中找到我们所需要的元素呢，这里就需要使用到选择器了，它们是用来定位元素并且提取元素的值。先来举几个例子看看：

* /html/head/title: 选择`<title>`节点, 它位于html文档的`<head>`节点内
* /html/head/title/text(): 选择上面的`<title>`节点的内容.
* //td: 选择页面中所有的<td>元素
* //div[@class="mine"]: 选择所有拥有属性`class="mine"`的div元素

Scrapy使用css和xpath选择器来定位元素，它有四个基本方法：

* xpath(): 返回选择器列表，每个选择器代表使用xpath语法选择的节点
* css(): 返回选择器列表，每个选择器代表使用css语法选择的节点
* extract(): 返回被选择元素的unicode字符串
* re(): 返回通过正则表达式提取的unicode字符串列表

## 使用选择器
下面我们通过Scrapy shell演示下选择器的使用，假设我们有如下的一个网页<http://doc.scrapy.org/en/latest/_static/selectors-sample1.html>，内容如下：
``` html
<html>
 <head>
  <base href='http://example.com/' />
  <title>Example website</title>
 </head>
 <body>
  <div id='images'>
   <a href='image1.html'>Name: My image 1 <br /><img src='image1_thumb.jpg' /></a>
   <a href='image2.html'>Name: My image 2 <br /><img src='image2_thumb.jpg' /></a>
   <a href='image3.html'>Name: My image 3 <br /><img src='image3_thumb.jpg' /></a>
   <a href='image4.html'>Name: My image 4 <br /><img src='image4_thumb.jpg' /></a>
   <a href='image5.html'>Name: My image 5 <br /><img src='image5_thumb.jpg' /></a>
  </div>
 </body>
</html>
```
首先我们打开shell
``` bash
scrapy shell http://doc.scrapy.org/en/latest/_static/selectors-sample1.html
```
运行
```
>>> response.xpath('//title/text()')
[<Selector (text) xpath=//title/text()>]
>>> response.css('title::text')
[<Selector (text) xpath=//title/text()>]
```
结果可以看出,`xpath()`和`css()`方法返回的是`SelectorList`实例，是一个选择器列表，你可以选择嵌套的数据：
```
>>> response.css('img').xpath('@src').extract()
[u'image1_thumb.jpg',
 u'image2_thumb.jpg',
 u'image3_thumb.jpg',
 u'image4_thumb.jpg',
 u'image5_thumb.jpg']
```
必须使用`.extract()`才能提取最终的数据，如果你只想获得第一个匹配的，可以使用`.extract_first()`
```
>>> response.xpath('//div[@id="images"]/a/text()').extract_first()
u'Name: My image 1 '
```
如果没有找到，会返回`None`，还可选择默认值
```
>>> response.xpath('//div[@id="not-exists"]/text()').extract_first(default='not-found')
'not-found'
```
而CSS选择器还可以使用CSS3标准：
```
>>> response.css('title::text').extract()
[u'Example website']
```
下面是几个比较全面的示例：
```
>>> response.xpath('//base/@href').extract()
[u'http://example.com/']

>>> response.css('base::attr(href)').extract()
[u'http://example.com/']

>>> response.xpath('//a[contains(@href, "image")]/@href').extract()
[u'image1.html',
 u'image2.html',
 u'image3.html',
 u'image4.html',
 u'image5.html']

>>> response.css('a[href*=image]::attr(href)').extract()
[u'image1.html',
 u'image2.html',
 u'image3.html',
 u'image4.html',
 u'image5.html']

>>> response.xpath('//a[contains(@href, "image")]/img/@src').extract()
[u'image1_thumb.jpg',
 u'image2_thumb.jpg',
 u'image3_thumb.jpg',
 u'image4_thumb.jpg',
 u'image5_thumb.jpg']

>>> response.css('a[href*=image] img::attr(src)').extract()
[u'image1_thumb.jpg',
 u'image2_thumb.jpg',
 u'image3_thumb.jpg',
 u'image4_thumb.jpg',
 u'image5_thumb.jpg']

```

## 嵌套选择器
`xpath()`和`css()`返回的是选择器列表，所以你可以继续使用它们的方法。举例来讲：
```
>>> links = response.xpath('//a[contains(@href, "image")]')
>>> links.extract()
[u'<a href="image1.html">Name: My image 1 <br><img src="image1_thumb.jpg"></a>',
 u'<a href="image2.html">Name: My image 2 <br><img src="image2_thumb.jpg"></a>',
 u'<a href="image3.html">Name: My image 3 <br><img src="image3_thumb.jpg"></a>',
 u'<a href="image4.html">Name: My image 4 <br><img src="image4_thumb.jpg"></a>',
 u'<a href="image5.html">Name: My image 5 <br><img src="image5_thumb.jpg"></a>']

>>> for index, link in enumerate(links):
...     args = (index, link.xpath('@href').extract(), link.xpath('img/@src').extract())
...     print 'Link number %d points to url %s and image %s' % args

Link number 0 points to url [u'image1.html'] and image [u'image1_thumb.jpg']
Link number 1 points to url [u'image2.html'] and image [u'image2_thumb.jpg']
Link number 2 points to url [u'image3.html'] and image [u'image3_thumb.jpg']
Link number 3 points to url [u'image4.html'] and image [u'image4_thumb.jpg']
Link number 4 points to url [u'image5.html'] and image [u'image5_thumb.jpg']
```
## 使用正则表达式
`Selector`有一个`re()`方法通过正则表达式提取数据，它返回的是unicode字符串列表，你不能再去嵌套使用
```
>>> response.xpath('//a[contains(@href, "image")]/text()').re(r'Name:\s*(.*)')
[u'My image 1',
 u'My image 2',
 u'My image 3',
 u'My image 4',
 u'My image 5']

>>> response.xpath('//a[contains(@href, "image")]/text()').re_first(r'Name:\s*(.*)')
u'My image 1'
```

## XPath相对路径
当你嵌套使用XPath时候，不要使用`/`开头的，因为这个会相对文档根节点开始算起，需要使用相对路径
```
>>> divs = response.xpath('//div')
>>> for p in divs.xpath('.//p'):  # extracts all <p> inside
...     print p.extract()

# 或者下面这个直接使用p也可以
>>> for p in divs.xpath('p'):
...     print p.extract()
```

## XPath建议

### 使用text作为条件时
避免使用`.//text()`,直接使用`.`
```
>>> sel.xpath("//a[contains(., 'Next Page')]").extract()
[u'<a href="#">Click here to go to the <strong>Next Page</strong></a>']
```

### //node[1]和(//node)[1]区别

* //node[1]: 选择所有位于第一个子节点位置的node节点
* (//node)[1]: 选择所有的node节点，然后返回结果中的第一个node节点

### 通过class查找时优先考虑CSS
```
>> from scrapy import Selector
>>> sel = Selector(text='<div class="hero shout"><time datetime="2014-07-23 19:00">Special date</time></div>')
>>> sel.css('.shout').xpath('./time/@datetime').extract()
[u'2014-07-23 19:00']
```

