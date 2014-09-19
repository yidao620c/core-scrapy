#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 糗事百科最新笑话
Desc : 
"""

import urllib2
import os.path
import contextlib

from scrapy import Spider
from scrapy import log

from scrapydemo.utils import *
from scrapydemo.items import *
from scrapydemo.settings import IMAGES_STORE


class JokerSpider(Spider):
    """xpath的一些常见复杂查找示例"""
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[1][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[3][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/strong/text()')
    # '//li[contains(@class, "nav_pro_item")]/div/a/img/@src[1]')
    # '//*[contains(@class, "nav_pro_text")]/a/@href')
    name = 'joker'
    allowed_domains = ['qiushibaike.com']
    start_urls = [
        'http://www.qiushibaike.com/late',
    ]

    def parse(self, response):
        # 抓取前6个笑话
        items = []
        jokelist = []
        for i in range(1, 7):
            i_xpath = response.xpath('//div[@id="content-left"]/div[%d]' % (i,))
            item = JokeItem()
            item['content'] = ltos(i_xpath.xpath(
                'div[@class="content"]/text()').extract()).encode('utf-8')
            img_src = None
            if i_xpath.xpath('div[@class="thumb"]'):
                item['image_urls'] = i_xpath.xpath(
                    'div[@class="thumb"]/a[1]/img/@src').extract()
                full_imgurl = item['image_urls'][0]
                img_src = full_imgurl
                filename = os.path.basename(item['image_urls'][0])
                log.msg('-------------' + full_imgurl, log.INFO)
                with contextlib.closing(urllib2.urlopen(full_imgurl)) as f:
                    with open(os.path.join(IMAGES_STORE, filename), 'wb') as bfile:
                        bfile.write(f.read())
            items.append(item)
            jokelist.append((item['content'], img_src))
        send_mail(jokelist)
        return items
