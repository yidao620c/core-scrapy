#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 定义数据库模型实体
Desc : 
"""

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from settings import DATABASE
import datetime

DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**DATABASE))


def create_news_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


def _get_date():
    return datetime.datetime.now()


# 定义新闻实体
class News(DeclarativeBase):
    """Sqlalchemy deals model"""
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

