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

from coolscrapy.utils import send_mail
from coolscrapy.items import *
from coolscrapy.settings import IMAGES_STORE


class JokerSpider(Spider):
    """xpath的一些常见复杂查找示例"""
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[1][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/br/following-sibling::node()[3][self::text()]')
    # '//*[contains(@class, "nav_pro_text")]/a/strong/text()')
    # '//li[contains(@class, "nav_pro_item")]/div/a/img/@src[1]')
    # '//*[contains(@class, "nav_pro_text")]/a/@href')
    name = 'joker'
    allowed_domains = ['xiaohua.com']
    start_urls = [
        'http://www.xiaohua.com/',
    ]

    def parse(self, response):
        # 抓取最新笑话
        items = []
        jokelist = []
        count = 1
        for jk in response.xpath('//div[starts-with(@class, "joke-box")]/ul/li[@class="t2"]'):
            if count > 10:
                break
            count += 1
            item = JokeItem()
            title = jk.xpath('*[1]/text()').extract_first()
            pic_content = jk.xpath('a[2]/img')
            txt_content = jk.xpath('a[2]/p')
            img_src = None
            if pic_content:
                item['image_urls'] = pic_content.xpath('@src').extract()
                full_imgurl = item['image_urls'][0]
                img_src = full_imgurl
                filename = os.path.basename(item['image_urls'][0])
                log.msg('-------------' + full_imgurl, log.INFO)
                with contextlib.closing(urllib2.urlopen(full_imgurl)) as f:
                    with open(os.path.join(IMAGES_STORE, filename), 'wb') as bfile:
                        bfile.write(f.read())
                item['content'] = ''
            else:
                item['content'] = '<br/>'.join(txt_content.xpath('text()').extract()).encode('utf-8')
            items.append(item)
            jokelist.append((item['content'], img_src))
        send_mail(jokelist)
        return items
