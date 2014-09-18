#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 糗事百科笑话
Desc : 
"""
import datetime

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy import Request, Spider
from scrapy import log
from scrapy.exceptions import DropItem
from scrapydemo.utils import *
from scrapydemo.items import *
from scrapydemo.utils import filter_tags
import urllib2
import os.path
import contextlib

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
        # 抓取前5个笑话
        for i in range(1, 6):
            item = JokeItem()
            i_xpath = response.xpath('//div[@id="content-left"]/div[%d]' % (i,))
            item['content'] = ltos(i_xpath.xpath('div[@class="content"]/text()').extract())
            if i_xpath.xpath('div[@class="thumb"]'):
                item['image_urls'] = i_xpath.xpath(
                    'div[@class="thumb"]/a[1]/img/@src').extract()
                full_imgurl = item['image_urls'][0]
                filename = os.path.basename(item['image_urls'][0])
                log.msg('-------------' + full_imgurl, log.INFO)
                with contextlib.closing(urllib2.urlopen(full_imgurl)) as f:
                    with open(os.path.join('D:/work', filename), 'wb') as bfile:
                        bfile.write(f.read())
            yield item
