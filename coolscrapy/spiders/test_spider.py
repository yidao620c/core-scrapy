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
    allowed_domains = ["jd.com"]
    start_urls = [
        "http://www.jd.com/"
    ]

    def parse(self, response):
        logging.info(u'---------我这个是简单的直接获取京东网首页测试---------')
        guessyou = response.xpath('//div[@id="guessyou"]/div[1]/h2/text()').extract_first()
        logging.info(u"find：%s" % guessyou)
        logging.info(u'---------------success----------------')

if __name__ == '__main__':
    body = u'发布于： 2016年04月08日'
    pat4 = re.compile(ur'\d{4}年\d{2}月\d{2}日')
    if (re.search(pat4, body)):
        print(re.search(pat4, body).group())
