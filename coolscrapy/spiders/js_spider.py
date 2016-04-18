#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 对于js异步加载网页的支持
Desc : 爬取京东网首页，下面内容基本都是异步加载的，我选取“猜你喜欢”这个异步加载内容来测试
"""
import logging
import re
import json
import base64
import scrapy
from scrapy_splash import SplashRequest


class JsSpider(scrapy.Spider):
    name = "jd"
    allowed_domains = ["jd.com"]
    start_urls = [
        "http://www.jd.com/"
    ]

    def start_requests(self):
        splash_args = {
            'wait': 0.5,
            # 'http_method': 'GET',
            # 'html': 1,
            # 'png': 1,
            # 'width': 600,
            # 'render_all': 1,
        }
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_result, endpoint='render.html',
                                args=splash_args)

    def parse_result(self, response):
        logging.info(u'----------使用splash爬取京东网首页异步加载内容-----------')
        guessyou = response.xpath('//div[@id="guessyou"]/div[1]/h2/text()').extract_first()
        logging.info(u"find：%s" % guessyou)
        logging.info(u'---------------success----------------')


if __name__ == '__main__':
    body = u'发布于： 2016年04月08日'
    pat4 = re.compile(ur'\d{4}年\d{2}月\d{2}日')
    if (re.search(pat4, body)):
        print(re.search(pat4, body).group())

