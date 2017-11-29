# Scrapy教程10- 动态配置爬虫

有很多时候我们需要从多个网站爬取所需要的数据，比如我们想爬取多个网站的新闻，将其存储到数据库同一个表中。我们是不是要对每个网站都得去定义一个Spider类呢？
其实不需要，我们可以通过维护一个规则配置表或者一个规则配置文件来动态增加或修改爬取规则，然后程序代码不需要更改就能实现多个网站爬取。

要这样做，我们就不能再使用前面的`scrapy crawl test`这种命令了，我们需要使用编程的方式运行Scrapy spider，参考[官方文档](http://doc.scrapy.org/en/1.0/topics/practices.html#run-scrapy-from-a-script)

### 脚本运行Scrapy
可以利用scrapy提供的[核心API](http://doc.scrapy.org/en/1.0/topics/api.html#topics-api)通过编程方式启动scrapy，代替传统的`scrapy crawl`启动方式。

Scrapy构建于Twisted异步网络框架基础之上，因此你需要在Twisted reactor里面运行。

首先你可以使用`scrapy.crawler.CrawlerProcess`这个类来运行你的spider，这个类会为你启动一个Twisted reactor，并能配置你的日志和shutdown处理器。所有的scrapy命令都使用这个类。
``` python
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl(MySpider)
process.start() # the script will block here until the crawling is finished

```
然后你就可以直接执行这个脚本
``` bash
python run.py
```

另外一个功能更强大的类是`scrapy.crawler.CrawlerRunner`，推荐你使用这个
``` python
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

class MySpider(scrapy.Spider):
    # Your spider definition
    ...

configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
runner = CrawlerRunner()

d = runner.crawl(MySpider)
d.addBoth(lambda _: reactor.stop())
reactor.run() # the script will block here until the crawling is finished
```

### 同一进程运行多个spider
默认情况当你每次执行`scrapy crawl`命令时会创建一个新的进程。但我们可以使用核心API在同一个进程中同时运行多个spider
``` python
import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

class MySpider1(scrapy.Spider):
    # Your first spider definition
    ...

class MySpider2(scrapy.Spider):
    # Your second spider definition
    ...

configure_logging()
runner = CrawlerRunner()
runner.crawl(MySpider1)
runner.crawl(MySpider2)
d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run() # the script will block here until all crawling jobs are finished
```

### 定义规则表
好了言归正传，有了前面的脚本启动基础，就可以开始我们的动态配置爬虫了。
我们的需求是这样的，从两个不同的网站爬取我们所需要的新闻文章，然后存储到article表中。

首先我们需要定义规则表和文章表，通过动态的创建蜘蛛类，我们以后就只需要维护规则表即可了。这里我使用SQLAlchemy框架来映射数据库。
``` python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 定义数据库模型实体
Desc :
"""
import datetime

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from coolscrapy.settings import DATABASE

Base = declarative_base()

class ArticleRule(Base):
    """自定义文章爬取规则"""
    __tablename__ = 'article_rule'

    id = Column(Integer, primary_key=True)
    # 规则名称
    name = Column(String(30))
    # 运行的域名列表，逗号隔开
    allow_domains = Column(String(100))
    # 开始URL列表，逗号隔开
    start_urls = Column(String(100))
    # 下一页的xpath
    next_page = Column(String(100))
    # 文章链接正则表达式(子串)
    allow_url = Column(String(200))
    # 文章链接提取区域xpath
    extract_from = Column(String(200))
    # 文章标题xpath
    title_xpath = Column(String(100))
    # 文章内容xpath
    body_xpath = Column(Text)
    # 发布时间xpath
    publish_time_xpath = Column(String(30))
    # 文章来源
    source_site = Column(String(30))
    # 规则是否生效
    enable = Column(Integer)


class Article(Base):
    """文章类"""
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(100))
    title = Column(String(100))
    body = Column(Text)
    publish_time = Column(String(30))
    source_site = Column(String(30))
```

### 定义文章Item
这个很简单了，没什么需要说明的
``` python
import scrapy


class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    publish_time = scrapy.Field()
    source_site = scrapy.Field()
```

### 定义ArticleSpider
接下来我们将定义爬取文章的蜘蛛，这个spider会使用一个Rule实例来初始化，然后根据Rule实例中的xpath规则来获取相应的数据。
``` python
from coolscrapy.utils import parse_text
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from coolscrapy.items import Article


class ArticleSpider(CrawlSpider):
    name = "article"

    def __init__(self, rule):
        self.rule = rule
        self.name = rule.name
        self.allowed_domains = rule.allow_domains.split(",")
        self.start_urls = rule.start_urls.split(",")
        rule_list = []
        # 添加`下一页`的规则
        if rule.next_page:
            rule_list.append(Rule(LinkExtractor(restrict_xpaths=rule.next_page)))
        # 添加抽取文章链接的规则
        rule_list.append(Rule(LinkExtractor(
            allow=[rule.allow_url],
            restrict_xpaths=[rule.extract_from]),
            callback='parse_item'))
        self.rules = tuple(rule_list)
        super(ArticleSpider, self).__init__()

    def parse_item(self, response):
        self.log('Hi, this is an article page! %s' % response.url)

        article = Article()
        article["url"] = response.url

        title = response.xpath(self.rule.title_xpath).extract()
        article["title"] = parse_text(title, self.rule.name, 'title')

        body = response.xpath(self.rule.body_xpath).extract()
        article["body"] = parse_text(body, self.rule.name, 'body')

        publish_time = response.xpath(self.rule.publish_time_xpath).extract()
        article["publish_time"] = parse_text(publish_time, self.rule.name, 'publish_time')

        article["source_site"] = self.rule.source_site

        return article
```
要注意的是start_urls，rules等都初始化成了对象的属性，都由传入的rule对象初始化，parse_item方法中的抽取规则也都有rule对象提供。

### 编写pipeline存储到数据库中
我们还是使用SQLAlchemy来将文章Item数据存储到数据库中
``` python
@contextmanager
def session_scope(Session):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class ArticleDataBasePipeline(object):
    """保存文章到数据库"""

    def __init__(self):
        engine = db_connect()
        create_news_table(engine)
        self.Session = sessionmaker(bind=engine)

    def open_spider(self, spider):
        """This method is called when the spider is opened."""
        pass

    def process_item(self, item, spider):
        a = Article(url=item["url"],
                    title=item["title"].encode("utf-8"),
                    publish_time=item["publish_time"].encode("utf-8"),
                    body=item["body"].encode("utf-8"),
                    source_site=item["source_site"].encode("utf-8"))
        with session_scope(self.Session) as session:
            session.add(a)

    def close_spider(self, spider):
        pass
```

### 修改run.py启动脚本
我们将上面的run.py稍作修改即可定制我们的文章爬虫启动脚本
``` python
import logging
from spiders.article_spider import ArticleSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from coolscrapy.models import db_connect
from coolscrapy.models import ArticleRule
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    settings = get_project_settings()
    configure_logging(settings)
    db = db_connect()
    Session = sessionmaker(bind=db)
    session = Session()
    rules = session.query(ArticleRule).filter(ArticleRule.enable == 1).all()
    session.close()
    runner = CrawlerRunner(settings)

    for rule in rules:
        # stop reactor when spider closes
        # runner.signals.connect(spider_closing, signal=signals.spider_closed)
        runner.crawl(ArticleSpider, rule=rule)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    # blocks process so always keep as the last statement
    reactor.run()
    logging.info('all finished.')
```

OK，一切搞定。现在我们可以往ArticleRule表中加入成百上千个网站的规则，而不用添加一行代码，就可以对这成百上千个网站进行爬取。
当然你完全可以做一个Web前端来完成维护ArticleRule表的任务。当然ArticleRule规则也可以放在除了数据库的任何地方，比如配置文件。

你可以在[GitHub](https://github.com/yidao620c/core-scrapy)上看到本文的完整项目源码。

