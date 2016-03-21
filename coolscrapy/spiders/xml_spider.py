#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 爬取XML订阅的蜘蛛
Desc : 
"""
from coolscrapy.items import BlogItem
import scrapy
from scrapy.spiders import XMLFeedSpider


class XMLSpider(XMLFeedSpider):
    name = "xml"
    allowed_domains = ["github.io"]
    start_urls = [
        "http://yidao620c.github.io/atom.xml"
    ]
    iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
    itertag = 'entry'

    def parse_node(self, response, node):
        self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

        item = BlogItem()
        item['title'] = node.xpath('title').extract()
        item['link'] = node.xpath('link/@href').extract()
        item['id'] = node.xpath('id').extract()
        item['published'] = node.xpath('published').extract()
        item['updated'] = node.xpath('updated').extract()
        print(item['title'],item['link'])
        return item

