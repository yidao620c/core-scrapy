#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 医药网络爬虫
Desc : 
"""
from scrapydemo.items import *
from scrapy.spider import Spider
from scrapy.contrib.spiders import XMLFeedSpider, CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector, HtmlXPathSelector
from scrapy.contrib.loader import ItemLoader
from scrapy import Request
from scrapy import log
from urlparse import urljoin
import uuid


class MedicineCrawlSpider(CrawlSpider):
    """网页爬虫"""
    name = 'drug39'
    allowed_domains = ['http://drug.39.net/']
    start_urls = [
        'http://drug.39.net/yjxw/yydt/index.html',
    ]
    rules = (
        # 提取匹配 '/Info/...' 的链接并使用spider的parse_item方法进行分析，并显式指定follow为True
        Rule(LinkExtractor(allow=(r'/a/\d{6}/\d+\.html', ), deny=('', )),
             callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        self.log('Hi, this is an item page! %s' % response.url, log.INFO)
        item = MedicineItem()
        item['id'] = uuid.uuid1()
        item['category'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['link'] = response.xpath('//td[@id="item_name"]/text()').extract()
        item['location'] = response.xpath('//td[@id="item_description"]/text()').extract()
        item['title'] = response.xpath('//td[@id="item_description"]/text()').extract()
        item['content'] = response.xpath('//td[@id="item_description"]/text()').extract()
        return item


class DiningXMLFeedSpider(XMLFeedSpider):
    """RSS/XML源爬虫"""
    name = 'dining_xml'
    allowed_domains = ['baidu.com']
    start_urls = [
        'http://news.baidu.com/',
        'http://tieba.baidu.com/',
        'http://home.baidu.com/',
    ]
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'item'

    def parse_node(self, response, node):
        self.log('Hi, this is a <%s> node!: %s' % (self.itertag, ''.join(node.extract())))

        item = Item()
        item['id'] = node.xpath('@id').extract()
        item['name'] = node.xpath('name').extract()
        item['description'] = node.xpath('description').extract()
        return item
