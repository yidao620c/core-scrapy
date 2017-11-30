# Scrapy教程03- Spider详解

Spider是爬虫框架的核心，爬取流程如下：

1. 先初始化请求URL列表，并指定下载后处理response的回调函数。初次请求URL通过`start_urls`指定，调用`start_requests()`产生`Request`对象，然后注册`parse`方法作为回调
1. 在parse回调中解析response并返回字典,`Item`对象,`Request`对象或它们的迭代对象。`Request`对象还会包含回调函数，之后Scrapy下载完后会被这里注册的回调函数处理。
1. 在回调函数里面，你通过使用选择器（同样可以使用BeautifulSoup,lxml或其他工具）解析页面内容，并生成解析后的结果Item。
1. 最后返回的这些Item通常会被持久化到数据库中(使用[Item Pipeline](http://doc.scrapy.org/en/latest/topics/item-pipeline.html#topics-item-pipeline))或者使用[Feed exports](http://doc.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-exports)将其保存到文件中。

尽管这个流程适合于所有的蜘蛛，但是Scrapy里面为不同的使用目的实现了一些常见的Spider。下面我们把它们列出来。

## CrawlSpider
链接爬取蜘蛛，专门为那些爬取有特定规律的链接内容而准备的。
如果你觉得它还不足以适合你的需求，可以先继承它然后覆盖相应的方法，或者自定义Spider也行。

它除了从`scrapy.Spider`类继承的属性外，还有一个新的属性`rules`,它是一个`Rule`对象列表，每个`Rule`对象定义了某个规则，如果多个`Rule`匹配一个连接，那么使用第一个，根据定义的顺序。

一个详细的例子：
``` python
from coolscrapy.items import HuxiuItem
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class LinkSpider(CrawlSpider):
    name = "link"
    allowed_domains = ["huxiu.com"]
    start_urls = [
        "http://www.huxiu.com/index.php"
    ]

    rules = (
        # 提取匹配正则式'/group?f=index_group'链接 (但是不能匹配'deny.php')
        # 并且会递归爬取(如果没有定义callback，默认follow=True).
        Rule(LinkExtractor(allow=('/group?f=index_group', ), deny=('deny\.php', ))),
        # 提取匹配'/article/\d+/\d+.html'的链接，并使用parse_item来解析它们下载后的内容，不递归
        Rule(LinkExtractor(allow=('/article/\d+/\d+\.html', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        detail = response.xpath('//div[@class="article-wrap"]')
        item = HuxiuItem()
        item['title'] = detail.xpath('h1/text()')[0].extract()
        item['link'] = response.url
        item['posttime'] = detail.xpath(
            'div[@class="article-author"]/span[@class="article-time"]/text()')[0].extract()
        print(item['title'],item['link'],item['posttime'])
        yield item

```

## XMLFeedSpider
XML订阅蜘蛛，用来爬取XML形式的订阅内容，通过某个指定的节点来遍历。
可使用`iternodes`, `xml`, 和`html`三种形式的迭代器，不过当内容比较多的时候推荐使用`iternodes`，
默认也是它，可以节省内存提升性能，不需要将整个DOM加载到内存中再解析。而使用`html`可以处理XML有格式错误的内容。
处理XML的时候最好先[Removing namespaces](http://doc.scrapy.org/en/1.0/topics/selectors.html#removing-namespaces)

接下来我通过爬取我的博客订阅XML来展示它的使用方法。
``` python
from coolscrapy.items import BlogItem
import scrapy
from scrapy.spiders import XMLFeedSpider


class XMLSpider(XMLFeedSpider):
    name = "xml"
    namespaces = [('atom', 'http://www.w3.org/2005/Atom')]
    allowed_domains = ["github.io"]
    start_urls = [
        "http://www.pycoding.com/atom.xml"
    ]
    iterator = 'xml'  # 缺省的iternodes，貌似对于有namespace的xml不行
    itertag = 'atom:entry'

    def parse_node(self, response, node):
        # self.logger.info('Hi, this is a <%s> node!', self.itertag)
        item = BlogItem()
        item['title'] = node.xpath('atom:title/text()')[0].extract()
        item['link'] = node.xpath('atom:link/@href')[0].extract()
        item['id'] = node.xpath('atom:id/text()')[0].extract()
        item['published'] = node.xpath('atom:published/text()')[0].extract()
        item['updated'] = node.xpath('atom:updated/text()')[0].extract()
        self.logger.info('|'.join([item['title'],item['link'],item['id'],item['published']]))
        return item
```

## CSVFeedSpider
这个跟上面的XMLFeedSpider很类似，区别在于它会一行一行的迭代，而不是一个节点一个节点的迭代。
每次迭代行的时候会调用`parse_row()`方法。
``` python
from coolscrapy.items import BlogItem
from scrapy.spiders import CSVFeedSpider


class CSVSpider(CSVFeedSpider):
    name = "csv"
    allowed_domains = ['example.com']
    start_urls = ['http://www.example.com/feed.csv']
    delimiter = ';'
    quotechar = "'"
    headers = ['id', 'name', 'description']

    def parse_row(self, response, row):
        self.logger.info('Hi, this is a row!: %r', row)
        item = BlogItem()
        item['id'] = row['id']
        item['name'] = row['name']
        return item
```

## SitemapSpider
站点地图蜘蛛，允许你使用[Sitemaps](http://www.sitemaps.org/)发现URL后爬取整个站点。
还支持嵌套的站点地图以及从`robots.txt`中发现站点URL

