# -*- coding: utf-8 -*-

# Scrapy settings for scrapydemo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'scrapydemo'

SPIDER_MODULES = ['scrapydemo.spiders']
NEWSPIDER_MODULE = 'scrapydemo.spiders'
# COMMANDS_MODULE = 'scrapydemo.commands'
# DEFAULT_ITEM_CLASS = 'scrapydemo.items.MyItem'

ITEM_PIPELINES = {
    # 'scrapydemo.pipelines.FilterWordsPipeline': 1,
    # 'scrapydemo.pipelines.JsonWriterPipeline': 2,
    # 'scrapydemo.pipelines.JsonExportPipeline': 3,
    # 'scrapydemo.pipelines.MyDatabasePipeline': 4,
    # 'scrapydemo.pipelines.MyImagesPipeline': 5,
}
DOWNLOADER_MIDDLEWARES = {
    # 这里是下载中间件
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'scrapydemo.middlewares.RotateUserAgentMiddleware': 400
}
SPIDER_MIDDLEWARES = {
    # 这是爬虫中间件， 543是运行的优先级
    # 'myproject.middlewares.UrlUniqueMiddleware': 543,
}
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'scrapydemo (+http://www.yourdomain.com)'
# USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.7'

# 几个反正被Ban的策略设置
DOWNLOAD_TIMEOUT = 20
DOWNLOAD_DELAY = 5
# 禁用Cookie
COOKIES_ENABLES = False

LOG_LEVEL = "INFO"
LOG_STDOUT = True
LOG_FILE = "log/spider.log"

# Postgresql配置，居然不支持charset参数
# DATABASE = {'drivername': 'postgres',
#             'host': '10.0.0.154',
#             'port': '5432',
#             'username': 'root',
#             'password': 'changeme',
#             'database': 'scrapy'}

# windows install http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python
# linux pip install MySQL-python
DATABASE = {'drivername': 'mysql',
            'host': '192.168.203.95',
            'port': '3306',
            'username': 'root',
            'password': 'mysql',
            'database': 'weiqiye',
            'query': {'charset': 'utf8'}}

# 图片下载设置
IMAGES_STORE = 'D:/work/zpics'
IMAGES_EXPIRES = 30  # 30天内抓取的都不会被重抓
# 图片链接前缀
URL_PREFIX = 'http://dev.wingarden.net/tpl/static/pushimgs/'

