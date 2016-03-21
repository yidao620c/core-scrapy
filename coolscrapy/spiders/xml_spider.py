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
    namespaces = [('atom', 'http://www.w3.org/2005/Atom')]
    allowed_domains = ["github.io"]
    start_urls = [
        "http://yidao620c.github.io/atom.xml"
    ]
    iterator = 'xml'  # default iternodes
    itertag = 'atom:entry'

    def parse_node(self, response, node):
        # self.logger.info('Hi, this is a <%s> node!', self.itertag)
        item = BlogItem()
        item['title'] = node.xpath('atom:title/text()')[0].extract()
        item['link'] = node.xpath('atom:link/@href')[0].extract()
        item['id'] = node.xpath('atom:id/text()')[0].extract()
        item['published'] = node.xpath('atom:published/text()')[0].extract()
        item['updated'] = node.xpath('atom:updated/text()')[0].extract()
        self.logger.info(item['title'],item['link'],item['id'],item['published'])
        return item

