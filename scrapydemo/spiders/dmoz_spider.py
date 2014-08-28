#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc : 
"""
from scrapydemo.items import *
from scrapy.spider import Spider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector, HtmlXPathSelector
from scrapy.http import Request
from scrapy import log
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.exceptions import DropItem
import uuid


class DmozSpider(Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/",
    ]

    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html

        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        sel = Selector(response)
        sites = sel.xpath('//ul[@class="directory-url"]/li')
        items = []

        for site in sites:
            title = site.xpath('a/text()').extract()
            link = site.xpath('a/@href').extract()
            desc = site.xpath('text()').re(r'-\s([^\n]*?)\n')
            items.append(MyItem(title=title, link=link, desc=desc))

        return items


class BaiduSpider(Spider):
    name = "baidu"
    allowed_domains = ["baidu.com"]
    start_urls = [
        "http://www.baidu.com/"
    ]

    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html

        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        self.log('parse.... %s' % (response.url,), log.INFO)
        title = response.xpath(u'//a[text()="关于百度"]/text()').extract()[0].encode('gb2312')
        self.log('========title=%s' % title, log.INFO)
        link = 'dddd'
        desc = 'ccccc'
        return MyItem(title=title, link=link, desc=desc)


class DrugTestSpider(Spider):
    name = "drugtest"
    allowed_domains = ["drug.39.net"]
    start_urls = [
        "http://drug.39.net/yjxw/yydt/index.html"
    ]

    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html

        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        self.log('parse.... %s' % (response.url,), log.INFO)
        title = response.xpath(u'//a[text()="尾页"]/text()').extract()[0]
        # 返回的是gb2312编码的unicode对象
        self.log('========title=%s' % title.encode('gb2312').decode('utf-8'), log.INFO)
        # str类型
        self.log('========type=%s' % type(title.encode('gb2312')), log.INFO)
        # 转换成utf-8编码后的unicode类型
        self.log('========type=%s' % type(title.encode('gb2312').decode('utf-8')), log.INFO)
        link = 'dddd'
        desc = 'ccccc'
        return MyItem(title=title, link=link, desc=desc)


class DrugLinkSpider(CrawlSpider):
    name = "druglink"
    #设置下载延时
    download_delay = 2
    allowed_domains = ["drug.39.net"]
    start_urls = [
        "http://drug.39.net/yjxw/yydt/index.html"
    ]
    rules = (
        # LxmlLinkExtractor提取链接列表
        Rule(LxmlLinkExtractor(allow=(r'yydt/index_\d+\.html', r'/a/\d{6}/\d+\.html'),
                               restrict_xpaths=(u'//a[text()="下一页"]', '//div[@class="listbox"]')),
             callback='parse_links', follow=True),
    )

    def parse_links(self, response):
        self.log('-------------------> link_list url=%s' % response.url, log.INFO)
        # 如果是首页文章链接，直接处理
        if '/a/' in response.url:
            yield self.parse_page(response)
        else:
            hxs = HtmlXPathSelector(response)
            links = hxs.xpath('//div[starts-with(@class, "listbox")]/ul/li/span/a')
            for link in links:
                url = link.xpath('@href').extract()[0]
                yield Request(url=url, callback=self.parse_page)

    countt = True

    def parse_page(self, response):
        try:
            self.log('-------------------> link_page url=%s' % response.url, log.INFO)
            item = MedicineItem()
            item['id'] = uuid.uuid1()
            item['category'] = response.xpath(
                '//span[@class="art_location"]/a[last()]/text()').extract()[0].encode('gb2312')
            item['link'] = response.url
            item['location'] = response.xpath('//div[@class="date"]/em[2]/a/text()|//div[@class='
                                              '"date"]/em[2]/text()').extract()[0].encode('gb2312')
            item['title'] = response.xpath('//h1/text()').extract()[0].encode('gb2312')
            item['content'] = "".join(response.xpath(
                '//div[@id="contentText"]/p//text()').extract()).encode('gb2312')
            self.log('!!!!!!! category=%s' % item['category'], log.INFO)
            self.log('!!!!!!! location=%s' % item['location'], log.INFO)
            self.log('!!!!!!! title=%s' % item['title'], log.INFO)
            if self.countt:
                self.log('!!!!!!! content=%s' % item['content'], log.INFO)
                self.countt = False
            return item
        except:
            self.log('ERROR----->>>>>>>>>%s' % response.url, log.INFO)
            return DropItem()
