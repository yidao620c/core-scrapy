#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc : 
"""
from scrapy import log
from scrapydemo.items import *
from scrapy.spider import Spider
from scrapy.contrib.spiders import XMLFeedSpider, CSVFeedSpider, CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.contrib.loader import ItemLoader
from scrapy import Request


class ItemLoaderSpider(Spider):
    """xpath的一些常见复杂查找示例"""
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[1][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[3][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/strong/text()')
    # '//li[contains(@class, "nav_pro_item")]/div/a/img/@src[1]')
    # '//*[contains(@class, "nav_pro_text")]/a/@href')
    name = 'itemloader'
    allowed_domains = ['baidu.com']
    start_urls = [
        'http://news.baidu.com/',
        'http://tieba.baidu.com/',
        'http://home.baidu.com/',
    ]

    @staticmethod
    def to_utf8(item, *attrs):
        for each_attr in attrs:
            each_val = item[each_attr]
            if isinstance(each_val, unicode):
                item[each_attr] = each_val.encode('utf-8')
            elif hasattr(each_val, '__iter__'):
                item[each_attr] = [v.encode('utf-8') for v in each_val]
        return item

    def parse(self, response):
        items = []
        for everyday in response.xpath('//ul/li/strong/a'):
            loader = XPathItemLoader(ProductItem(), everyday)
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()
            loader.add_xpath('name', 'text()')
            loader.add_xpath('price', '@href')
            loader.add_xpath('stock', '@mon')
            loader.add_value('last_updated', 'today')  # you can also use literal values
            item = self.to_utf8(loader.load_item(), *['name', 'price', 'stock', 'last_updated'])
            self.log(item['name'], log.ERROR)
            items.append(item)
        return items


class MyCrawlSpider(CrawlSpider):
    """普通网页爬虫"""
    name = 'crawl'
    allowed_domains = ['baidu.com']
    start_urls = [
        'http://news.baidu.com/',
        'http://tieba.baidu.com/',
        'http://home.baidu.com/',
    ]
    rules = (
        # 提取匹配 'xxx' (但不匹配 'yyy') 的链接
        # 并跟进链接(没有callback意味着follow默认为True)
        # Rule(LinkExtractor(allow=('xxx', ), deny=('yyy', ))),

        # 提取匹配 '/Info/...' 的链接并使用spider的parse_item方法进行分析，并显式指定follow为True
        Rule(LinkExtractor(allow=(r'/Info/\d{4}/\d+\.htm', ), deny=('', )),
             callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        self.log('Hi, this is an item page! %s' % response.url, log.INFO)

        item = MyItem()
        item['title'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['link'] = response.xpath('//td[@id="item_name"]/text()').extract()
        item['desc'] = response.xpath('//td[@id="item_description"]/text()').extract()
        return item


class MyXMLFeedSpider(XMLFeedSpider):
    """RSS/XML源爬虫"""
    name = 'xmlfeed'
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


class MyCSVFeedSpider(CSVFeedSpider):
    """CSV源爬虫"""
    name = 'csvfeed'
    allowed_domains = ['baidu.com']
    start_urls = [
        'http://news.baidu.com/',
        'http://tieba.baidu.com/',
        'http://home.baidu.com/',
    ]
    delimiter = ';'
    headers = ['id', 'name', 'description']

    def parse_row(self, response, row):
        self.log('Hi, this is a row!: %r' % row, log.INFO)

        item = Item()
        item['id'] = row['id']
        item['name'] = row['name']
        item['description'] = row['description']
        return item
