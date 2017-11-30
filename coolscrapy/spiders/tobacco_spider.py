#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 烟草条形码爬虫
-- 烟草表
DROP TABLE IF EXISTS `t_tobacco`;
CREATE TABLE `t_tobacco` (
  `id`                        BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
  `product_name`              VARCHAR(32)  COMMENT '产品名称',
  `brand`                     VARCHAR(32)  COMMENT '品牌',
  `product_type`              VARCHAR(32)  COMMENT '产品类型',
  `package_spec`              VARCHAR(64)  COMMENT '包装规格',
  `reference_price`           VARCHAR(32)  COMMENT '参考价格',
  `manufacturer`              VARCHAR(32)  COMMENT '生产厂家',
  `pics`                      VARCHAR(255) COMMENT '图片URL',
  `created_time`              DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time`              DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='烟草表';

-- 烟草条形码表
DROP TABLE IF EXISTS `t_barcode`;
CREATE TABLE `t_barcode` (
  `id`                        BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
  `tobacco_id`                BIGINT COMMENT '香烟产品ID',
  `barcode`                   VARCHAR(32) COMMENT '条形码',
  `btype`                     VARCHAR(32) COMMENT '类型 小盒条形码/条包条形码',
  `created_time`              DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time`              DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='烟草条形码表';
"""
from scrapy import Request

from coolscrapy.utils import parse_text, tx
from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.linkextractors import LinkExtractor
from coolscrapy.items import Article, TobaccoItem


class TobaccoSpider(Spider):
    """
    爬取本页面内容，然后再提取下一页链接生成新的Request标准做法
    另外还使用了图片下载管道
    """
    name = "tobacco"
    allowed_domains = ["etmoc.com"]
    base_url = "http://www.etmoc.com/market/Brandlist.asp"
    start_urls = [
        "http://www.etmoc.com/market/Brandlist.asp?page=86&worded=&temp="
    ]
    pics_pre = 'http://www.etmoc.com/'

    def parse(self, response):
        # 处理本页内容
        for item in self.parse_page(response):
            yield item
        # 找下一页链接递归爬
        next_url = tx(response.xpath('//a[text()="【下一页】"]/@href'))
        if next_url:
            self.logger.info('+++++++++++next_url++++++++++=' + self.base_url + next_url)
            yield Request(url=self.base_url + next_url, meta={'ds': "ds"}, callback=self.parse)

    def parse_page(self, response):
        self.logger.info('Hi, this is a page = %s', response.url)
        items = []
        for ind, each_row in enumerate(response.xpath('//div[@id="mainlist"]/table/tbody/tr')):
            if ind == 0:
                continue
            item = TobaccoItem()
            item['pics'] = self.pics_pre + tx(each_row.xpath('td[1]/a/img/@src'))[3:]
            product_name = tx(each_row.xpath('td[2]/p[1]/text()'))
            brand = tx(each_row.xpath('td[2]/p[2]/a/text()'))
            barcode1 = tx(each_row.xpath('td[2]/p[3]/text()'))
            barcode2 = tx(each_row.xpath('td[2]/p[4]/text()'))
            item['product'] = "{}/{}/{}/{}".format(product_name, brand, barcode1, barcode2)
            item['product_type'] = tx(each_row.xpath('td[3]/text()'))
            item['package_spec'] = tx(each_row.xpath('td[4]/text()'))
            item['reference_price'] = tx(each_row.xpath('td[5]/span/text()'))
            # 生产厂家有可能包含<a>链接，我取里面的文本，使用//text()
            item['manufacturer'] = tx(each_row.xpath('td[6]//text()'))
            self.logger.info("pics={},product={},product_type={},package_spec={},"
                             "reference_price={},manufacturer={}".format(
                item['pics'], item['product'], item['product_type'], item['package_spec']
                , item['reference_price'], item['manufacturer']))
            items.append(item)
        return items
