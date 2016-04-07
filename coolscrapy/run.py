#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc : 
"""

from coolscrapy.models import ArticleRule
from spiders.article_spider import DeepSpider
import logging

from twisted.internet import reactor
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging, logger
from scrapy.utils.project import get_project_settings
from coolscrapy.models import db_connect


def spider_closing(spider):
    """Activates on spider closed signal"""
    logger.msg("Spider closed: %s" % spider, level=logging.INFO)

configure_logging()
settings = get_project_settings()

db = db_connect()
rules = db.query(ArticleRule).filter(ArticleRule.enable == 1)
runner = CrawlerRunner(settings)

for rule in rules:
    spider = DeepSpider(rule)  # instantiate every spider using rule
    # stop reactor when spider closes
    # runner.signals.connect(spider_closing, signal=signals.spider_closed)
    runner.crawl(spider)

d = runner.join()
d.addBoth(lambda _: reactor.stop())

# blocks process so always keep as the last statement
reactor.run()

