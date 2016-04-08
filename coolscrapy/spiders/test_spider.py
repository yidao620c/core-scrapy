#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 爬虫小测试类
Desc : 
"""
import logging
import scrapy


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["huxiu.com"]
    start_urls = [
        "http://www.huxiu.com/article/144610/1.html?f=index_feed_article"
    ]

    def parse(self, response):
        body = response.xpath('//div[@id="article_content"]/p/text()').extract()
        if body:
            for b in body:
                print(b)
        print('---------------result----------------')
        result = '\n'.join(body) if body else ""
        logging.info(result)


