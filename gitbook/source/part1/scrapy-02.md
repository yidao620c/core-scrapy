# Scrapy教程02- 完整示例

这篇文章我们通过一个比较完整的例子来教你使用Scrapy，我选择爬取[虎嗅网首页](http://www.huxiu.com/)的新闻列表。

这里我们将完成如下几个步骤：

* 创建一个新的Scrapy工程
* 定义你所需要要抽取的Item对象
* 编写一个spider来爬取某个网站并提取出所有的Item对象
* 编写一个Item Pipline来存储提取出来的Item对象

Scrapy使用Python语言编写，如果你对这门语言还不熟，请先去学习下基本知识。

## 创建Scrapy工程

在任何你喜欢的目录执行如下命令
``` bash
scrapy startproject coolscrapy
```
将会创建coolscrapy文件夹，其目录结构如下：
```
coolscrapy/
    scrapy.cfg            # 部署配置文件

    coolscrapy/           # Python模块，你所有的代码都放这里面
        __init__.py

        items.py          # Item定义文件

        pipelines.py      # pipelines定义文件

        settings.py       # 配置文件

        spiders/          # 所有爬虫spider都放这个文件夹下面
            __init__.py
            ...
```

## 定义我们的Item
我们通过创建一个scrapy.Item类，并定义它的类型为scrapy.Field的属性，
我们准备将虎嗅网新闻列表的名称、链接地址和摘要爬取下来。

``` python
import scrapy

class HuxiuItem(scrapy.Item):
    title = scrapy.Field()    # 标题
    link = scrapy.Field()     # 链接
    desc = scrapy.Field()     # 简述
    posttime = scrapy.Field() # 发布时间
```

也许你觉得定义这个Item有点麻烦，但是定义完之后你可以得到许多好处，这样你就可以使用Scrapy中其他有用的组件和帮助类。

## 第一个Spider
蜘蛛就是你定义的一些类，Scrapy使用它们来从一个domain（或domain组）爬取信息。
在蜘蛛类中定义了一个初始化的URL下载列表，以及怎样跟踪链接，如何解析页面内容来提取Item。

定义一个Spider，只需继承`scrapy.Spider`类并定于一些属性：

* name: Spider名称，必须是唯一的
* start_urls: 初始化下载链接URL
* parse(): 用来解析下载后的Response对象，该对象也是这个方法的唯一参数。
它负责解析返回页面数据并提取出相应的Item（返回Item对象），还有其他合法的链接URL（返回Request对象）。

我们在coolscrapy/spiders文件夹下面新建`huxiu_spider.py`，内容如下：
``` python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc :
"""
from coolscrapy.items import HuxiuItem
import scrapy

class HuxiuSpider(scrapy.Spider):
    name = "huxiu"
    allowed_domains = ["huxiu.com"]
    start_urls = [
        "http://www.huxiu.com/index.php"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="mod-info-flow"]/div/div[@class="mob-ctt"]'):
            item = HuxiuItem()
            item['title'] = sel.xpath('h3/a/text()')[0].extract()
            item['link'] = sel.xpath('h3/a/@href')[0].extract()
            url = response.urljoin(item['link'])
            item['desc'] = sel.xpath('div[@class="mob-sub"]/text()')[0].extract()
            print(item['title'],item['link'],item['desc'])
```

## 运行爬虫
在根目录执行下面的命令，其中huxiu是你定义的spider名字：
```
scrapy crawl huxiu
```
如果一切正常，应该可以打印出每一个新闻

## 处理链接
如果想继续跟踪每个新闻链接进去，看看它的详细内容的话，那么可以在parse()方法中返回一个Request对象，
然后注册一个回调函数来解析新闻详情。

``` python
from coolscrapy.items import HuxiuItem
import scrapy

class HuxiuSpider(scrapy.Spider):
    name = "huxiu"
    allowed_domains = ["huxiu.com"]
    start_urls = [
        "http://www.huxiu.com/index.php"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="mod-info-flow"]/div/div[@class="mob-ctt"]'):
            item = HuxiuItem()
            item['title'] = sel.xpath('h3/a/text()')[0].extract()
            item['link'] = sel.xpath('h3/a/@href')[0].extract()
            url = response.urljoin(item['link'])
            item['desc'] = sel.xpath('div[@class="mob-sub"]/text()')[0].extract()
            # print(item['title'],item['link'],item['desc'])
            yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        detail = response.xpath('//div[@class="article-wrap"]')
        item = HuxiuItem()
        item['title'] = detail.xpath('h1/text()')[0].extract()
        item['link'] = response.url
        item['posttime'] = detail.xpath(
            'div[@class="article-author"]/span[@class="article-time"]/text()')[0].extract()
        print(item['title'],item['link'],item['posttime'])
        yield item
```
现在parse只提取感兴趣的链接，然后将链接内容解析交给另外的方法去处理了。
你可以基于这个构建更加复杂的爬虫程序了。

## 导出抓取数据
最简单的保存抓取数据的方式是使用json格式的文件保存在本地，像下面这样运行：
``` bash
scrapy crawl huxiu -o items.json
```
在演示的小系统里面这种方式足够了。不过如果你要构建复杂的爬虫系统，
最好自己编写[Item Pipeline](http://doc.scrapy.org/en/latest/topics/item-pipeline.html#topics-item-pipeline)。

## 保存数据到数据库
上面我们介绍了可以将抓取的Item导出为json格式的文件，不过最常见的做法还是编写Pipeline将其存储到数据库中。我们在`coolscrapy/pipelines.py`定义
``` python
# -*- coding: utf-8 -*-
import datetime
import redis
import json
import logging
from contextlib import contextmanager

from scrapy import signals
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from coolscrapy.models import News, db_connect, create_news_table, Article


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
上面我使用了python中的SQLAlchemy来保存数据库，这个是一个非常优秀的ORM库，我写了篇关于它的[入门教程](http://yidao620c.github.io/2016/03/07/sqlalchemy.html)，可以参考下。

然后在`setting.py`中配置这个Pipeline，还有数据库链接等信息：
``` python
ITEM_PIPELINES = {
    'coolscrapy.pipelines.ArticleDataBasePipeline': 5,
}

# linux pip install MySQL-python
DATABASE = {'drivername': 'mysql',
            'host': '192.168.203.95',
            'port': '3306',
            'username': 'root',
            'password': 'mysql',
            'database': 'spider',
            'query': {'charset': 'utf8'}}
```
再次运行爬虫
``` bash
scrapy crawl huxiu
```
那么所有新闻的文章都存储到数据库中去了。

## 下一步
本章只是带你领略了scrapy最基本的功能，还有很多高级特性没有讲到。接下来会通过多个例子向你展示scrapy的其他特性，然后再深入讲述每个特性。

