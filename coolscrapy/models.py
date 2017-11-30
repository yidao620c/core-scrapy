#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 定义数据库模型实体
Desc : 
"""
import datetime

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from coolscrapy.settings import DATABASE


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**DATABASE))


def create_news_table(engine):
    """"""
    Base.metadata.create_all(engine)


def _get_date():
    return datetime.datetime.now()

Base = declarative_base()


class ArticleRule(Base):
    """自定义文章爬取规则"""
    __tablename__ = 'article_rule'

    id = Column(Integer, primary_key=True)
    # 规则名称
    name = Column(String(30))
    # 运行的域名列表，逗号隔开
    allow_domains = Column(String(100))
    # 开始URL列表，逗号隔开
    start_urls = Column(String(100))
    # 下一页的xpath
    next_page = Column(String(100))
    # 文章链接正则表达式(子串)
    allow_url = Column(String(200))
    # 文章链接提取区域xpath
    extract_from = Column(String(200))
    # 文章标题xpath
    title_xpath = Column(String(100))
    # 文章内容xpath
    body_xpath = Column(Text)
    # 发布时间xpath
    publish_time_xpath = Column(String(30))
    # 文章来源
    source_site = Column(String(30))
    # 规则是否生效
    enable = Column(Integer)


class Article(Base):
    """文章类"""
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(100))
    title = Column(String(100))
    body = Column(Text)
    publish_time = Column(String(30))
    source_site = Column(String(30))


class News(Base):
    """定义新闻实体"""
    __tablename__ = "wqy_push_essay"
    # 主键
    id = Column(Integer, primary_key=True)
    # 爬虫key
    crawlkey = Column('crawlkey', String(30), nullable=True)
    # 新闻分类
    category = Column('category', String(40), nullable=True)
    # 新闻链接地址
    link = Column('link', String(120), nullable=True)
    # 新闻来源
    location = Column('location', String(60), nullable=True)
    # 发布时间
    pubdate = Column('pubdate', DateTime, default=_get_date)
    # 新闻标题
    title = Column('title', String(120), nullable=True)
    # 正文
    content = Column('content', Text, nullable=True)
    # 带html标签的正文
    htmlcontent = Column('htmlcontent', Text, nullable=True)


class Tobacco(Base):
    """烟草"""
    __tablename__ = 't_tobacco'

    id = Column(Integer, primary_key=True)
    product_name = Column(String(32))
    brand = Column(String(32))
    product_type = Column(String(16))
    package_spec = Column(String(32))
    reference_price = Column(String(32))
    manufacturer = Column(String(32))
    pics = Column(String(255))
    created_time = Column(DateTime, default=_get_date)
    updated_time = Column(DateTime, default=_get_date)


class Barcode(Base):
    """烟草条形码"""
    __tablename__ = 't_barcode'

    id = Column(Integer, primary_key=True)
    tobacco_id = Column(Integer)
    barcode = Column(String(32))
    btype = Column(String(32))
    created_time = Column(DateTime, default=_get_date)
    updated_time = Column(DateTime, default=_get_date)
