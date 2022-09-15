import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "jav"

SPIDER_MODULES = ['jav.spiders']
NEWSPIDER_MODULE = 'jav.spiders'

ITEM_PIPELINES = {
    'jav.pipelines.PgsqlPipeline': 1,          # store to postgresql
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'jav.middlewares.JavSpiderMiddleware': 1,
    'jav.middlewares.ProxySpiderMiddleware': 2,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
}

PG_URI = "postgresql://username:password@host/jav" if not "PG_URI" in os.environ or os.environ[
    "PG_URI"] is None else os.environ["PG_URI"]

# Proxy 
# 默认不使用代理
# PROXY = 'http://127.0.0.1:7890'
