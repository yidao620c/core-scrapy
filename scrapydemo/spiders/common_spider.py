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
# """RSS/XML源爬虫，一般都是从一个列表开始爬，然后一个个的打开网页"""
# name = 'xmlfeed'
# allowed_domains = ['http://drug.39.net/']
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
    allowed_domains = ["drug.39.net"]
    start_urls = [
        "http://drug.39.net/yjxw/yydt/index.html"
    ]
    rules = (
        # LxmlLinkExtractor提取链接列表
        Rule(LxmlLinkExtractor(allow=(r'/yydt/index_\d+\.html', r'/a/\d{6}/\d+\.html'),
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
    """医药网pharmnet.com.cn"""
    name = 'pharmnet'
    allowed_domains = ['pharmnet.com.cn']
    start_urls = [
        'http://news.pharmnet.com.cn/news/hyyw/news/index0.html',
        'http://news.pharmnet.com.cn/news/hyyw/news/index1.html',
    ]

    rules = (
        # LxmlLinkExtractor提取链接列表
        Rule(LxmlLinkExtractor(allow=(r'/news/\d{4}/\d{2}/\d{2}/\d+\.html'
                                      , r'/news/hyyw/news/index\d+\.html')
                               , restrict_xpaths=('//div[@class="list"]', '//div[@class="page"]'))
             , callback='parse_links', follow=False),
    )

    def parse_links(self, response):
        # 如果是首页文章链接，直接处理
        if '/hyyw/' not in response.url:
            yield self.parse_page(response)
        else:
            self.log('-------------------> link_list url=%s' % response.url, log.INFO)
            links = response.xpath('//div[@class="list"]/ul/li/p/a')
            for link in links:
                url = link.xpath('@href').extract()[0]
                yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            self.log('-------------------> link_page url=%s' % response.url, log.INFO)
            item = NewsItem()
            item['crawlkey'] = self.name
            item['category'] = ltos(response.xpath(
                '//div[@class="current"]/a[last()]/text()').extract())
            item['link'] = response.url
            head_line = ltos(response.xpath('//div[@class="ct01"]/text()[1]').extract())
            item['location'] = head_line.strip().split()[1]
            item['pubdate'] = datetime.datetime.strptime(head_line.strip().split()[0], '%Y-%m-%d')
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@class="ct02"]/font/div/div|//div[@class="ct02"]/font/div').extract()])
            item['content'] = filter_tags(content_temp)
            self.log('########title=%s' % item['title'].encode('gb2312'), log.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, log.INFO)
            raise DropItem('DropItem-----%s' % response.url)
