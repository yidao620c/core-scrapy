#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 定义数据库模型实体
Desc : 
"""
import datetime
from contextlib import contextmanager

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
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


class Rule(Base):
    __tablename__ = 'rules'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    name = Column(String)
    allow_domains = Column(String)
    start_urls = Column(String)
    next_page = Column(String)
    allow_url = Column(String)
    extract_from = Column(String)
    title_xpath = Column(String)
    body_xpath = Column(String)
    publish_time_xpath = Column(String)
    source_site_xpath = Column(String)
    enable = Column(Integer)


class ArticleRule(Base):
    """自定义文章爬取规则"""
    __tablename__ = 'article_rule'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    allow_domains = Column(String)
    start_urls = Column(String)
    next_page = Column(String)
    allow_url = Column(String)
    extract_from = Column(String)
    title_xpath = Column(String)
    body_xpath = Column(String)
    publish_time_xpath = Column(String)
    source_site_xpath = Column(String)
    enable = Column(Integer)


class Article(Base):
    """文章类"""
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    body = Column(String)
    publish_time = Column(String)
    source_site = Column(String)


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

