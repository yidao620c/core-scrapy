# Scrapy教程07- 内置服务

Scrapy使用Python内置的的日志系统来记录事件日志。
日志配置
``` python
LOG_ENABLED = true
LOG_ENCODING = "utf-8"
LOG_LEVEL = logging.INFO
LOG_FILE = "log/spider.log"
LOG_STDOUT = True
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"
```
使用也很简单
``` python
import logging
logger = logging.getLogger(__name__)
logger.warning("This is a warning")
```

如果在Spider里面使用，那就更简单了，因为logger就是它的一个实例变量
``` python
import scrapy

class MySpider(scrapy.Spider):

    name = 'myspider'
    start_urls = ['http://scrapinghub.com']

    def parse(self, response):
        self.logger.info('Parse function called on %s', response.url)
```

## 发送email
Scrapy发送email基于[Twisted non-blocking IO](http://twistedmatrix.com/documents/current/core/howto/defer-intro.html)实现，只需几个简单配置即可。

初始化
``` python
mailer = MailSender.from_settings(settings)
```
发送不包含附件
``` python
mailer.send(to=["someone@example.com"], subject="Some subject", body="Some body", cc=["another@example.com"])
```
配置
``` python
MAIL_FROM = 'scrapy@localhost'
MAIL_HOST = 'localhost'
MAIL_PORT = 25
MAIL_USER = ""
MAIL_PASS = ""
MAIL_TLS = False
MAIL_SSL = False
```

## 同一个进程运行多个Spider
``` python
import scrapy
from scrapy.crawler import CrawlerProcess

class MySpider1(scrapy.Spider):
    # Your first spider definition
    ...

class MySpider2(scrapy.Spider):
    # Your second spider definition
    ...

process = CrawlerProcess()
process.crawl(MySpider1)
process.crawl(MySpider2)
process.start() # the script will block here until all crawling jobs are finished

```

## 分布式爬虫
Scrapy并没有提供内置的分布式抓取功能，不过有很多方法可以帮你实现。

如果你有很多个spider，最简单的方式就是启动多个`Scrapyd`实例，然后将spider分布到各个机器上面。

如果你想多个机器运行同一个spider，可以将url分片后交给每个机器上面的spider。比如你把URL分成3份
```
http://somedomain.com/urls-to-crawl/spider1/part1.list
http://somedomain.com/urls-to-crawl/spider1/part2.list
http://somedomain.com/urls-to-crawl/spider1/part3.list
```
然后运行3个`Scrapyd`实例，分别启动它们，并传递part参数
```
curl http://scrapy1.mycompany.com:6800/schedule.json -d project=myproject -d spider=spider1 -d part=1
curl http://scrapy2.mycompany.com:6800/schedule.json -d project=myproject -d spider=spider1 -d part=2
curl http://scrapy3.mycompany.com:6800/schedule.json -d project=myproject -d spider=spider1 -d part=3
```

## 防止被封的策略
一些网站实现了一些策略来禁止爬虫来爬取它们的网页。有的比较简单，有的相当复杂，如果你需要详细了解可以咨询[商业支持](http://scrapy.org/support/)

下面是对于这些网站的一些有用的建议：

* 使用user agent池。也就是每次发送的时候随机从池中选择不一样的浏览器头信息，防止暴露爬虫身份
* 禁止Cookie，某些网站会通过Cookie识别用户身份，禁用后使得服务器无法识别爬虫轨迹
* 设置download_delay下载延迟，数字设置为5秒，越大越安全
* 如果有可能的话尽量使用[Google cache](http://www.googleguide.com/cached_pages.html)获取网页，而不是直接访问
* 使用一个轮转IP池，例如免费的[Tor project](https://www.torproject.org/)或者是付费的[ProxyMesh](http://proxymesh.com/)
* 使用大型分布式下载器，这样就能完全避免被封了，只需要关注怎样解析页面就行。一个例子就是[Crawlera](http://scrapinghub.com/crawlera)

如果这些还是无法避免被禁，可以考虑[商业支持](http://scrapy.org/support/)

