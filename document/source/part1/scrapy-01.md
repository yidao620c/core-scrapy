# Scrapy教程01- 入门篇

Scrapy是一个为了爬取网站数据，提取结构性数据而编写的应用框架。可以应用在包括数据挖掘，
信息处理或存储历史数据等一系列的程序中。其最初是为了页面抓取(更确切来说,网络抓取)所设计的，
也可以应用在获取API所返回的数据(比如Web Services)或者通用的网络爬虫。

Scrapy也能帮你实现高阶的爬虫框架，比如爬取时的网站认证、内容的分析处理、重复抓取、分布式爬取等等很复杂的事。

## 安装scrapy

我的测试环境是centos6.5

升级python到最新版的2.7，下面的所有步骤都切换到root用户

由于scrapy目前只能运行在python2上，所以先更新centos上面的python到最新的
[Python 2.7.11](https://www.python.org/downloads/release/python-2711/)，
具体方法请google下很多这样的教程。

先安装一些依赖软件
```
yum install python-devel
yum install libffi-devel
yum install openssl-devel
```

然后安装pyopenssl库
```
pip install pyopenssl
```

安装xlml
```
yum install python-lxml
yum install libxml2-devel
yum install libxslt-devel
```

安装service-identity
```
pip install service-identity
```

安装twisted
```
pip install scrapy
```

安装scrapy
```
pip install scrapy -U
```

测试scrapy
```
scrapy bench
```

最终成功，太不容易了！

## 简单示例

创建一个python源文件，名为stackoverflow.py，内容如下：

``` python
import scrapy


class StackOverflowSpider(scrapy.Spider):
    name = 'stackoverflow'
    start_urls = ['http://stackoverflow.com/questions?sort=votes']

    def parse(self, response):
        for href in response.css('.question-summary h3 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_question)

    def parse_question(self, response):
        yield {
            'title': response.css('h1 a::text').extract()[0],
            'votes': response.css('.question .vote-count-post::text').extract()[0],
            'body': response.css('.question .post-text').extract()[0],
            'tags': response.css('.question .post-tag::text').extract(),
            'link': response.url,
        }
```
运行：
```
scrapy runspider stackoverflow_spider.py -o top-stackoverflow-questions.json
```

结果类似下面：
```
[{
    "body": "... LONG HTML HERE ...",
    "link": "http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array",
    "tags": ["java", "c++", "performance", "optimization"],
    "title": "Why is processing a sorted array faster than an unsorted array?",
    "votes": "9924"
},
{
    "body": "... LONG HTML HERE ...",
    "link": "http://stackoverflow.com/questions/1260748/how-do-i-remove-a-git-submodule",
    "tags": ["git", "git-submodules"],
    "title": "How do I remove a Git submodule?",
    "votes": "1764"
},
...]
```

当你运行`scrapy runspider somefile.py`这条语句的时候，Scrapy会去寻找源文件中定义的一个spider并且交给爬虫引擎来执行它。
`start_urls`属性定义了开始的URL，爬虫会通过它来构建初始的请求，返回response后再调用默认的回调方法`parse`并传入这个response。
我们在`parse`回调方法中通过使用css选择器提取每个提问页面链接的href属性值，然后`yield`另外一个请求，
并注册`parse_question`回调方法，在这个请求完成后被执行。

处理流程图：

![scrapy架构图](/source/images/scrapy.png)

Scrapy的一个好处是所有请求都是被调度并异步处理，就算某个请求出错也不影响其他请求继续被处理。

我们的示例中将解析结果生成json格式，你还可以导出为其他格式（比如XML、CSV），或者是将其存储到FTP、Amazon S3上。
你还可以通过[pipeline](http://doc.scrapy.org/en/1.0/topics/item-pipeline.html#topics-item-pipeline)
将它们存储到数据库中去，这些数据保存的方式各种各样。

## Scrapy特性一览
你已经可以通过Scrapy从一个网站上面爬取数据并将其解析保存下来了，但是这只是Scrapy的皮毛。
Scrapy提供了更多的特性来让你爬取更加容易和高效。比如：

1. 内置支持扩展的CSS选择器和XPath表达式来从HTML/XML源码中选择并提取数据，还能使用正则表达式
2. 提供交互式shell控制台试验CSS和XPath表达式，这个在调试你的蜘蛛程序时很有用
1. 内置支持生成多种格式的订阅导出（JSON、CSV、XML）并将它们存储在多个位置（FTP、S3、本地文件系统）
1. 健壮的编码支持和自动识别，用于处理外文、非标准和错误编码问题
1. 可扩展，允许你使用[signals](http://doc.scrapy.org/en/1.0/topics/signals.html#topics-signals)
和友好的API(middlewares, extensions, 和pipelines)来编写自定义插件功能。
1. 大量的内置扩展和中间件供使用：
    - cookies and session handling
    - HTTP features like compression, authentication, caching
    - user-agent spoofing
    - robots.txt
    - crawl depth restriction
    - and more
1. 还有其他好多好东东，比如可重复利用蜘蛛来爬取[Sitemaps](http://www.sitemaps.org/)和XML/CSV订阅，
一个跟爬取元素关联的媒体管道来
[自动下载图片](http://doc.scrapy.org/en/1.0/topics/media-pipeline.html#topics-media-pipeline)，
一个缓存DNS解析器等等。

