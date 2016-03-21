# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HuxiuItem(scrapy.Item):
    title = scrapy.Field()      # 标题
    link = scrapy.Field()       # 链接
    desc = scrapy.Field()       # 简述
    published = scrapy.Field()  # 发布时间


class BlogItem(scrapy.Item):
    title = scrapy.Field()      # 标题
    link = scrapy.Field()       # 链接
    id = scrapy.Field()         # ID号
    published = scrapy.Field()  # 发布时间
    updated = scrapy.Field()    # 更新时间


