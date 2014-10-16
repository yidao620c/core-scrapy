# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import Request
from scrapy import signals
from scrapy.contrib.exporter import JsonItemExporter
from scrapy import log
import json
import datetime
from sqlalchemy.orm import sessionmaker
from models import News, db_connect, create_news_table
from scrapy.contrib.pipeline.images import ImagesPipeline


class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion', 'pilgrim']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if False:
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item


class JsonWriterPipeline(object):
    """
    The purpose of JsonWriterPipeline is just to introduce how to write item pipelines.
    If you really want to store all scraped items into a JSON file you should use the Feed exports.
    """

    def __init__(self):
        pass
        # self.file = open('items.json', 'wb')

    def open_spider(self, spider):
        """This method is called when the spider is opened."""
        log.msg('open_spider....', level=log.INFO)

    def process_item(self, item, spider):
        log.msg('process_item....', level=log.INFO)
        # line = json.dumps(dict(item)) + "\n"
        # self.file.write(line)
        return item

    def close_spider(self, spider):
        """This method is called when the spider is closed."""
        log.msg('close_spider....', level=log.INFO)
        # self.file.close()


class JsonExportPipeline(object):
    def __init__(self):
        log.msg('JsonExportPipeline.init....', level=log.INFO)
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        log.msg('JsonExportPipeline.from_crawler....', level=log.INFO)
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        log.msg('JsonExportPipeline.spider_opened....', level=log.INFO)
        file = open('%s.json' % spider.name, 'w+b')
        self.files[spider] = file
        self.exporter = JsonItemExporter(file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        log.msg('JsonExportPipeline.spider_closed....', level=log.INFO)
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        log.msg('JsonExportPipeline.process_item....', level=log.INFO)
        self.exporter.export_item(item)
        return item


class MyDatabasePipeline(object):
    """抓取数据保存到数据库管道"""

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_news_table(engine)
        # 初始化对象属性Session为可调用对象
        self.Session = sessionmaker(bind=engine)
        self.recent_links = None
        self.nowtime = datetime.datetime.now()

    def open_spider(self, spider):
        """This method is called when the spider is opened."""
        log.msg('open_spider[%s]....' % spider.name, level=log.INFO)
        session = self.Session()
        recent_news = session.query(News).filter(
            News.crawlkey == spider.name ,
            self.nowtime - News.pubdate <= datetime.timedelta(days=30)).all()
        self.recent_links = [t.link for t in recent_news]
        print(self.recent_links)

    def process_item(self, item, spider):
        """Save deals in the database.
        This method is called for every item pipeline component.
        """
        # 每次获取到Item调用这个callable，获得一个新的session
        log.msg('mysql->%s' % item['link'], log.INFO)
        if item['link'] not in self.recent_links:
            session = self.Session()
            news = News(**item)
            try:
                session.add(news)
                session.commit()
                self.recent_links.append(item['link'])
            except:
                session.rollback()
                raise
            finally:
                session.close()
        return item


class MyImagesPipeline(ImagesPipeline):
    """先安装：pip install Pillow"""
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item
