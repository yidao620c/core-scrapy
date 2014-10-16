# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join


class MyItem(Item):
    title = Field()
    link = Field()
    desc = Field()


class ProductItem(Item):
    name = Field()
    price = Field()
    stock = Field()
    last_updated = Field(serializer=str)


class NewsItem(Item):
    crawlkey = Field()  # 爬虫key
    category = Field()  # 新闻分类
    link = Field()  # 新闻链接地址
    location = Field()  # 新闻来源
    pubdate = Field()  # 发布时间
    title = Field()  # 新闻标题
    content = Field()  # 正文
    htmlcontent = Field()  # 带html标签的正文


class JokeItem(Item):
    content = Field()
    image_urls = Field()
    images = Field()