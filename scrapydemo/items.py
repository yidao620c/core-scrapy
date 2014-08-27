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


class MedicineItem(Item):
    id = Field()  # 主键
    category = Field()  # 新闻分类
    link = Field()  # 新闻链接地址
    location = Field()  # 新闻来源
    title = Field()  # 新闻标题
    content = Field()  # 正文