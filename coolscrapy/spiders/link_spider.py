#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 爬取链接的蜘蛛
Desc : 
"""
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
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('/group?f=index_group', ), deny=('subsection\.php', ))),
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('/article/\d+/\d+.html?f=index_feed_article', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        detail = response.xpath('//div[@class="article-wrap"]')
        item = HuxiuItem()
        item['title'] = detail.xpath('h1/text()')[0].extract()
        item['link'] = response.url
        item['posttime'] = detail.xpath(
            'div[@class="article-author"]/span[@class="article-time"]/text()')[0].extract()
        print(item['title'],item['link'],item['posttime'])
        yield item
