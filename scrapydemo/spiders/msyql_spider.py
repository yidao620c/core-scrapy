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
from scrapydemo.utils import *
import datetime
import re


class CnyywXMLFeedSpider(CrawlSpider):
    """RSS/XML源爬虫，从医药网cn-yyw.cn上面订阅行业资讯"""
    name = 'cnyywfeed'
    allowed_domains = ['cn-yyw.cn']
    start_urls = [
        'http://www.cn-yyw.cn/feed/rss.php?mid=21',
    ]

    def parse(self, response):
        item_xpaths = response.xpath('//channel/item')
        for i_xpath in item_xpaths:
            xitem = NewsItem()
            xitem['crawlkey'] = self.name
            xitem['title'] = ltos(i_xpath.xpath('title/text()').extract())
            self.log('title=%s' % xitem['title'].encode('utf-8'), log.INFO)
            xitem['link'] = ltos(i_xpath.xpath('link/text()').extract())
            self.log('link=%s' % xitem['link'], log.INFO)
            pubdate_temp = ltos(i_xpath.xpath('pubDate/text()').extract()).split(r' ')[0]
            self.log('pubdate=%s' % pubdate_temp, log.INFO)
            xitem['pubdate'] = pubdate_temp
            self.log('((((^_^))))'.center(50, '-'), log.INFO)
            yield Request(url=xitem['link'], meta={'item': xitem}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        page_item = response.meta['item']
        try:
            self.log('-------------------> link_page url=%s' % page_item['link'], log.INFO)
            page_item['category'] = ltos(response.xpath(
                '//div[@class="pos"]/a[last()]/text()').extract())
            page_item['location'] = ltos(response.xpath(
                '//div[@class="info"]/a/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@id="article"]').extract()])
            re_con_strong = re.compile(r'</strong>(\s*)<strong>')
            content_temp = re_con_strong.sub(r'\1', content_temp)
            re_start_strong = re.compile(r'<strong>', re.I)
            content_temp = re_start_strong.sub('<p>', content_temp)
            re_end_strong = re.compile(r'</strong>', re.I)
            content_temp = re_end_strong.sub('</p>', content_temp)
            page_item['content'] = filter_tags(content_temp)
            return page_item
        except:
            self.log('ERROR-----%s' % response.url, log.INFO)
            return None


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
                '//div[@class="date"]/em[2]/a/text()'
                '|//div[@class="date"]/em[2]/text()').extract())
            pubdate_temp = ltos(response.xpath('//div[@class="date"]/em[1]/text()').extract())
            item['pubdate'] = pubdate_temp
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@id="contentText"]/p').extract()])
            item['content'] = filter_tags(content_temp)
            self.log('########title=%s' % item['title'].encode('utf-8'), log.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, log.INFO)
            return None


def convert(item):
    item['crawlkey'] = item['crawlkey'].encode('utf-8')
    item['category'] = item['category'].encode('utf-8')
    item['link'] = item['link'].encode('utf-8')
    item['location'] = item['location'].encode('utf-8')
    item['pubdate'] = item['pubdate'].encode('utf-8')
    item['title'] = item['title'].encode('utf-8')
    item['content'] = item['content'].encode('utf-8')


class PharmnetCrawlSpider(CrawlSpider):
    """医药网pharmnet.com.cn"""
    name = 'pharmnet'
    allowed_domains = ['pharmnet.com.cn']
    start_urls = [
        'http://news.pharmnet.com.cn/news/hyyw/news/index0.html',
        # 'http://news.pharmnet.com.cn/news/hyyw/news/index1.html',
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
            item['pubdate'] = head_line.strip().split()[0]
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@class="ct02"]/font/div/div|//div[@class="ct02"]/font/div').extract()])
            item['content'] = filter_tags(content_temp)
            self.log('########title=%s' % item['title'].encode('utf-8'), log.INFO)
            convert(item)
            return item
        except:
            self.log('ERROR-----%s' % response.url, log.INFO)
            raise DropItem('DropItem-----%s' % response.url)
