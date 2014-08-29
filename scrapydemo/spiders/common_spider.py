#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 网络爬虫
Desc : 
"""
from scrapydemo.items import *
from scrapy.spider import Spider
from scrapy.contrib.spiders import XMLFeedSpider, CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector, HtmlXPathSelector
from scrapy.contrib.loader import ItemLoader
from scrapy import Request
from scrapy import log
from scrapy.exceptions import DropItem
from urlparse import urljoin
from scrapydemo.utils import filter_tags
import datetime


def ltos(lst):
    """列表取第一个值"""
    if lst is not None and isinstance(lst, list):
        if len(lst) > 0:
            return lst[0]
    return ''


# class CommonXMLFeedSpider(XMLFeedSpider):
#     """RSS/XML源爬虫，一般都是从一个列表开始爬，然后一个个的打开网页"""
#     name = 'xmlfeed'
#     allowed_domains = ['http://drug.39.net/']
#     start_urls = [
#         'http://drug.39.net/yjxw/yydt/index.html',
#     ]
#     iterator = 'iternodes'  # This is actually unnecessary, since it's the default value
#     itertag = 'item'
#
#     def parse_node(self, response, node):
#         self.log('Hi, this is a <%s> node!: %s' % (self.itertag, ''.join(node.extract())))
#
#         item = Item()
#         item['id'] = node.xpath('@id').extract()
#         item['name'] = node.xpath('name').extract()
#         item['description'] = node.xpath('description').extract()
#         return item


class Drug39Spider(CrawlSpider):
    name = "drug39"
    # 设置下载延时
    download_delay = 2
    allowed_domains = ["drug.39.net"]
    start_urls = [
        "http://drug.39.net/yjxw/yydt/index.html"
    ]
    rules = (
        # LxmlLinkExtractor提取链接列表
        Rule(LxmlLinkExtractor(allow=(r'yydt/index_\d+\.html', r'/a/\d{6}/\d+\.html'),
                               # restrict_xpaths=(u'//a[text()="下一页"]', '//div[@class="listbox"]')),
                               restrict_xpaths=('//div[@class="listbox"]',)),
             callback='parse_links', follow=False),
    )

    def parse_links(self, response):
        # 如果是首页文章链接，直接处理
        if '/a/' in response.url:
            yield self.parse_page(response)
        else:
            self.log('-------------------> link_list url=%s' % response.url, log.INFO)
            links = response.xpath('//div[starts-with(@class, "listbox")]/ul/li/span/a')
            for link in links:
                url = link.xpath('@href').extract()[0]
                yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            self.log('-------------------> link_page url=%s' % response.url, log.INFO)
            item = NewsItem()
            item['crawlkey'] = self.name
            item['category'] = ltos(response.xpath(
                '//span[@class="art_location"]/a[last()]/text()').extract())
            item['link'] = response.url
            item['location'] = ltos(response.xpath(
                '//div[@class="date"]/em[2]/a/text()|//div[@class="date"]/em[2]/text()').extract())
            pubdate_temp = ltos(response.xpath('//div[@class="date"]/em[1]/text()').extract())
            item['pubdate'] = datetime.datetime.strptime(pubdate_temp, '%Y-%m-%d')
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@id="contentText"]/p').extract()])
            item['content'] = filter_tags(content_temp)
            self.log('########title=%s' % item['title'].encode('gb2312'), log.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, log.INFO)
            return None


class PharmnetCrawlSpider(CrawlSpider):
    """pharmnet网页爬虫"""
    name = 'pharmnet'
    allowed_domains = ['http://news.pharmnet.com.cn/']
    start_urls = [
        'http://news.pharmnet.com.cn/news/hyyw/news/index0.html',
    ]

    def parse(self, response):
        self.log('Hi, this is an item page! %s' % response.url, log.INFO)
        news_links = response.xpath('//div[@class="list"]/ul/li/p/a')
        for each_link in news_links:
            url = ltos(each_link.xpath('@href').extract())
            yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            self.log('-------------------> link_page url=%s' % response.url, log.INFO)
            item = NewsItem()
            item['category'] = "医药资讯"
            item['link'] = response.url
            item['location'] = '39健康网'
            item['pubdate'] = '2014/08/04'
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            item['content'] = "".join(response.xpath(
                '//div[@class="ct02"]/font/div//text()').extract())
            self.log('!!!!!!! title=%s' % item['title'].encode('gb2312'), log.INFO)
            return item
        except:
            self.log('ERROR----->>>>>>>>>%s' % response.url, log.INFO)
            return None
