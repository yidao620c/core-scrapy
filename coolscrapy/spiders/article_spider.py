#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc : 
"""

from coolscrapy.utils import parse_text
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from coolscrapy.items import Article


class ArticleSpider(CrawlSpider):
    name = "article"

    def __init__(self, rule):
        self.rule = rule
        self.name = rule.name
        self.allowed_domains = rule.allow_domains.split(",")
        self.start_urls = rule.start_urls.split(",")
        rule_list = []
        # 添加`下一页`的规则
        if rule.next_page:
            rule_list.append(Rule(LinkExtractor(restrict_xpaths=rule.next_page)))
        # 添加抽取文章链接的规则
        rule_list.append(Rule(LinkExtractor(
            allow=[rule.allow_url],
            restrict_xpaths=[rule.extract_from]),
            callback='parse_item'))
        self.rules = tuple(rule_list)
        super(ArticleSpider, self).__init__()

    def parse_item(self, response):
        self.log('Hi, this is an article page! %s' % response.url)

        article = Article()
        article["url"] = response.url

        title = response.xpath(self.rule.title_xpath).extract()
        article["title"] = parse_text(title, self.rule.name, 'title')

        body = response.xpath(self.rule.body_xpath).extract()
        article["body"] = parse_text(body, self.rule.name, 'body')

        publish_time = response.xpath(self.rule.publish_time_xpath).extract()
        article["publish_time"] = parse_text(publish_time, self.rule.name, 'publish_time')

        article["source_site"] = self.rule.source_site

        return article
