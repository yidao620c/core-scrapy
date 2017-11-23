# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    publish_time = scrapy.Field()
    source_site = scrapy.Field()


class NewsItem(scrapy.Item):
    """医药网新闻Item"""
    crawlkey = scrapy.Field()      # 关键字
    title = scrapy.Field()         # 标题
    link = scrapy.Field()          # 链接
    desc = scrapy.Field()          # 简述
    pubdate = scrapy.Field()       # 发布时间
    category = scrapy.Field()      # 分类
    location = scrapy.Field()      # 来源
    content = scrapy.Field()       # 内容
    htmlcontent = scrapy.Field()   # html内容


class HuxiuItem(scrapy.Item):
    """虎嗅网新闻Item"""
    title = scrapy.Field()      # 标题
    link = scrapy.Field()       # 链接
    desc = scrapy.Field()       # 简述
    published = scrapy.Field()  # 发布时间


class BlogItem(scrapy.Item):
    """博客Item"""
    title = scrapy.Field()      # 标题
    link = scrapy.Field()       # 链接
    id = scrapy.Field()         # ID号
    published = scrapy.Field()  # 发布时间
    updated = scrapy.Field()    # 更新时间


class JokeItem(scrapy.Item):
    """糗事百科笑话Item"""
    content = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class TobaccoItem(scrapy.Item):
    """烟草条形码Item"""
    pics = scrapy.Field()             # 图片
    product = scrapy.Field()          # 产品
    product_type = scrapy.Field()     # 产品类型
    package_spec = scrapy.Field()     # 包装规格
    reference_price = scrapy.Field()  # 参考零售价格
    manufacturer = scrapy.Field()     # 生产厂家
