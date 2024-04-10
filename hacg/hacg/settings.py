import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "hacg"

SPIDER_MODULES = ['hacg.spiders']
NEWSPIDER_MODULE = 'hacg.spiders'

ITEM_PIPELINES = {
    # 'hacg.pipelines.JsonWriterPipeline': 1,    # store to a json file
    'hacg.pipelines.PgsqlPipeline': 10,          # store to postgresql
}

PG_URI = os.environ['PG_URI']

HACG_ANIME_URL = "https://www.hacg.mov/wp/anime.html"
