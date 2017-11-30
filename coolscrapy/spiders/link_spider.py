#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 爬取链接的蜘蛛
Desc : 
"""
import logging
from coolscrapy.items import HuxiuItem
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class LinkSpider(CrawlSpider):
    name = "link"
    allowed_domains = ["huxiu.com"]
    start_urls = [
        "http://www.huxiu.com/index.php"
    ]

    rules = (
        # 提取匹配正则式'/group?f=index_group'链接 (但是不能匹配'deny.html')
        # 并且会递归爬取(如果没有定义callback，默认follow=True).
        Rule(LinkExtractor(allow=('/group?f=index_group', ), deny=('deny\.html', ))),
        # 提取匹配'/article/\d+/\d+.html'的链接，并使用parse_item来解析它们下载后的内容，不递归
        Rule(LinkExtractor(allow=('/article/\d+/\d+\.html', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        detail = response.xpath('//div[@class="article-wrap"]')
        item = HuxiuItem()
        item['title'] = detail.xpath('h1/text()')[0].extract()
        item['link'] = response.url
        item['published'] = detail.xpath(
            'div[@class="article-author"]/span[@class="article-time"]/text()')[0].extract()
        logging.info(item['title'],item['link'],item['published'])
        yield item


