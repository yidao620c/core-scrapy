# #!/usr/bin/env python
# # -*- encoding: utf-8 -*-
# """
# Topic: 网络爬虫
# Desc :
# """
from ..items import *
from scrapy.spiders import Spider
from scrapy.spiders import XMLFeedSpider, CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector, HtmlXPathSelector
from scrapy.loader import ItemLoader
from scrapy import Request
from scrapy.exceptions import DropItem
from urlparse import urljoin
from coolscrapy.utils import *
from datetime import datetime
import coolscrapy.settings as setting
import re
import uuid
import urllib2
import contextlib
import os
import logging


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
            self.log('title=%s' % xitem['title'].encode('utf-8'), logging.INFO)
            xitem['link'] = ltos(i_xpath.xpath('link/text()').extract())
            self.log('link=%s' % xitem['link'], logging.INFO)
            pubdate_temp = ltos(i_xpath.xpath('pubDate/text()').extract())
            self.log('pubdate=%s' % pubdate_temp, logging.INFO)
            xitem['pubdate'] = datetime.strptime(pubdate_temp, '%Y-%m-%d %H:%M:%S')
            self.log('((((^_^))))'.center(50, '-'), logging.INFO)
            yield Request(url=xitem['link'], meta={'item': xitem}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        page_item = response.meta['item']
        try:
            self.log('-------------------> link_page url=%s' % page_item['link'], logging.INFO)
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
            page_item['htmlcontent'] = page_item['content']
            return page_item
        except:
            self.log('ERROR-----%s' % response.url, logging.ERROR)
            return None


class Drug39Spider(Spider):
    name = "drug39"
    allowed_domains = ["drug.39.net"]
    start_urls = [
        "http://drug.39.net/yjxw/yydt/index.html"
    ]

    def parse(self, response):
        self.log('-------------------> link_list url=%s' % response.url, logging.INFO)
        links = response.xpath('//div[starts-with(@class, "listbox")]/ul/li')
        for link in links:
            url = link.xpath('span[1]/a/@href').extract()[0]
            date_str = link.xpath('span[2]/text()').extract()[0]
            date_str = date_str.split(' ')[1] + ':00'
            self.log('+++++++++++' + date_str, logging.INFO)
            yield Request(url=url, meta={'ds': date_str}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        dstr = response.meta['ds']
        try:
            self.log('-------------------> link_page url=%s' % response.url, logging.INFO)
            item = NewsItem()
            item['crawlkey'] = self.name
            item['category'] = ltos(response.xpath(
                '//span[@class="art_location"]/a[last()]/text()').extract())
            item['link'] = response.url
            item['location'] = ltos(response.xpath(
                '//div[@class="date"]/em[2]/a/text()'
                '|//div[@class="date"]/em[2]/text()').extract())
            pubdate_temp = ltos(response.xpath('//div[@class="date"]/em[1]/text()').extract())
            item['pubdate'] = datetime.strptime(pubdate_temp + ' ' + dstr, '%Y-%m-%d %H:%M:%S')
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@id="contentText"]/p').extract()])
            item['content'] = filter_tags(content_temp)
            htmlcontent = ltos(response.xpath('//div[@id="contentText"]').extract())
            item['htmlcontent'] = clean_html(htmlcontent)
            # 特殊构造，不作为分组
            # (?=...)之后的字符串需要匹配表达式才能成功匹配
            # (?<=...)之前的字符串需要匹配表达式才能成功匹配
            pat_img = re.compile(r'(<img (?:.|\n)*?src=")((.|\n)*?)(?=")')
            uuids = []
            for i, m in enumerate(pat_img.finditer(htmlcontent)):
                full_path = m.group(2)
                suffix_name = '.' + os.path.basename(full_path).split('.')[-1]
                uuid_name = '{0:02d}{1:s}'.format(i + 1, uuid.uuid4().hex) + suffix_name
                uuids.append(uuid_name)
                self.log('UUID_PIC--------%s' % setting.URL_PREFIX + uuid_name, logging.INFO)
                with contextlib.closing(urllib2.urlopen(full_path)) as f:
                    with open(os.path.join(IMAGES_STORE, uuid_name), 'wb') as bfile:
                        bfile.write(f.read())
            for indx, val in enumerate(uuids):
                htmlcontent = pat_img.sub(Nth(indx + 1, setting.URL_PREFIX + val), htmlcontent)
            item['htmlcontent'] = htmlcontent
            self.log('+++++++++title=%s+++++++++' % item['title'].encode('utf-8'), logging.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, logging.ERROR)
            return None


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
                               , restrict_xpaths=('//div[@class="list"]',
                                                  '//div[@class="page"]'))
             , callback='parse_links', follow=False),
    )

    def parse_links(self, response):
        # 如果是首页文章链接，直接处理
        if '/hyyw/' not in response.url:
            yield self.parse_page(response)
        else:
            self.log('-------------------> link_list url=%s' % response.url, logging.INFO)
            links = response.xpath('//div[@class="list"]/ul/li/p/a')
            for link in links:
                url = link.xpath('@href').extract()[0]
                yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            self.log('-------------------> link_page url=%s' % response.url, logging.INFO)
            item = NewsItem()
            item['crawlkey'] = self.name
            item['category'] = ltos(response.xpath(
                '//div[@class="current"]/a[last()]/text()').extract())
            item['link'] = response.url
            head_line = ltos(response.xpath('//div[@class="ct01"]/text()[1]').extract())
            item['location'] = head_line.strip().split()[1]
            item['pubdate'] = datetime.strptime(head_line.strip().split()[0], '%Y-%m-%d')
            item['title'] = ltos(response.xpath('//h1/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//div[@class="ct02"]/font/div/div|//div[@class="ct02"]/font/div').extract()])
            item['content'] = filter_tags(content_temp)
            hc = ltos(response.xpath('//div[@class="ct02"]').extract())
            htmlcontent = clean_html(hc)
            # 特殊构造，不作为分组
            # (?=...)之后的字符串需要匹配表达式才能成功匹配
            # (?<=...)之前的字符串需要匹配表达式才能成功匹配
            pat_img = re.compile(r'(<img (?:.|\n)*?src=")((.|\n)*?)(?=")')
            uuids = []
            for i, m in enumerate(pat_img.finditer(htmlcontent)):
                full_path = m.group(2)
                suffix_name = '.' + os.path.basename(full_path).split('.')[-1]
                uuid_name = '{0:02d}{1:s}'.format(i + 1, uuid.uuid4().hex) + suffix_name
                uuids.append(uuid_name)
                self.log('UUID_PIC--------%s' % setting.URL_PREFIX + uuid_name, logging.INFO)
                with contextlib.closing(urllib2.urlopen(full_path)) as f:
                    with open(os.path.join(IMAGES_STORE, uuid_name), 'wb') as bfile:
                        bfile.write(f.read())
            for indx, val in enumerate(uuids):
                htmlcontent = pat_img.sub(Nth(indx + 1, setting.URL_PREFIX + val), htmlcontent)
            item['htmlcontent'] = htmlcontent
            self.log('+++++++++title=%s+++++++++' % item['title'].encode('utf-8'), logging.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, logging.ERROR)
            raise DropItem('DropItem-----%s' % response.url)


class HaoyaoCrawlSpider(Spider):
    """医药咨询网http://www.haoyao.net/"""
    name = 'haoyao'
    allowed_domains = ['haoyao.net']
    start_urls = [
        'http://www.haoyao.net/news/cate----0----index.htm',
    ]

    def parse(self, response):
        self.log('-------------------> link_list url=%s' % response.url, logging.INFO)
        links = response.xpath('//div[@class="list"]')
        for link in links:
            url = link.xpath('div[1]/a/@href').extract()[0]
            url = 'http://www.haoyao.net/news/' + url.split('/')[-1]
            self.log('+++++++++++url=' + url, logging.INFO)
            date_str = (link.xpath('div[2]/text()').extract()[0]).strip() + ' 00:00:00'
            self.log('+++++++++++date_str=' + date_str, logging.INFO)
            yield Request(url=url, meta={'ds': date_str}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        dstr = response.meta['ds']
        try:
            self.log('-------------------> link_page url=%s' % response.url, logging.INFO)
            item = NewsItem()
            item['crawlkey'] = self.name
            item['category'] = '医药新闻'
            item['link'] = response.url
            item['location'] = ltos(response.xpath('//font[@color="#666666"]/a/text()').extract())
            item['pubdate'] = datetime.strptime(dstr, '%Y-%m-%d %H:%M:%S')
            item['title'] = ltos(response.xpath('//span[@id="lblTitle"]/text()').extract())
            content_temp = "".join([tt.strip() for tt in response.xpath(
                '//span[@id="spContent"]/p').extract()])
            item['content'] = filter_tags(content_temp)
            htmlcontent = ltos(response.xpath('//div[@id="divContent"]').extract())
            item['htmlcontent'] = clean_html(htmlcontent)
            # 特殊构造，不作为分组
            # (?=...)之后的字符串需要匹配表达式才能成功匹配
            # (?<=...)之前的字符串需要匹配表达式才能成功匹配
            pat_img = re.compile(r'(<img (?:.|\n)*?src=")((.|\n)*?)(?=")')
            uuids = []
            for i, m in enumerate(pat_img.finditer(htmlcontent)):
                full_path = 'http://www.haoyao.net' + m.group(2)
                suffix_name = '.' + os.path.basename(full_path).split('.')[-1]
                uuid_name = '{0:02d}{1:s}'.format(i + 1, uuid.uuid4().hex) + suffix_name
                uuids.append(uuid_name)
                self.log('UUID_PIC--------%s' % setting.URL_PREFIX + uuid_name, logging.INFO)
                with contextlib.closing(urllib2.urlopen(full_path)) as f:
                    with open(os.path.join(IMAGES_STORE, uuid_name), 'wb') as bfile:
                        bfile.write(f.read())
            for indx, val in enumerate(uuids):
                htmlcontent = pat_img.sub(Nth(indx + 1, setting.URL_PREFIX + val), htmlcontent)
            item['htmlcontent'] = htmlcontent
            self.log('+++++++++title=%s+++++++++' % item['title'].encode('utf-8'), logging.INFO)
            return item
        except:
            self.log('ERROR-----%s' % response.url, logging.ERROR)
            return None


class Nth(object):
    """
    如果 sub 函数的第二个参数是个函数，则每次匹配到的时候都会执行这个函数。
    函数接受匹配到的那个 match object 作为参数，返回用来替换的字符串。
    利用这个特性就可以只在第 N 次匹配的时候返回要替换成的字符串，其他时候原样返回不做替换即可。
    """

    def __init__(self, nth, replacement):
        self.nth = nth
        self.replacement = replacement
        self.calls = 0

    def __call__(self, matchobj):
        self.calls += 1
        if self.calls == self.nth:
            return matchobj.group(1) + self.replacement
        return matchobj.group(0)
