#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 爬虫小测试类
Desc : 
"""
import logging
import scrapy
import re


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["oschina.net"]
    start_urls = [
        "http://www.oschina.net/news/72297/csharp-7-features-preview"
    ]

    def parse(self, response):
        body = response.xpath('//div[@class="PubDate"]/text()').extract()
        body2 = body.encode('utf-8')
        pat4 = re.compile(r'\d{4}年\d{2}月\d{2}日')
        if (re.search(pat4, body)):
            print('body...')
        if (re.search(pat4, body2)):
            print('body2222222222222')
        logging.info('---------------success----------------')

if __name__ == '__main__':
    body = '发布于： 2016年04月08日'
    pat4 = re.compile(r'\d{4}年\d{2}月\d{2}日')
    if (re.search(pat4, body)):
        print(re.search(pat4, body).group())
