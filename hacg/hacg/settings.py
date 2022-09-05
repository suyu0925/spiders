import os

BOT_NAME = "hacg"

SPIDER_MODULES = ['hacg.spiders']
NEWSPIDER_MODULE = 'hacg.spiders'

ITEM_PIPELINES = {
    # 'hacg.pipelines.JsonWriterPipeline': 1,    # store to a json file
    'hacg.pipelines.MongoPipeline': 10,          # store to mongodb
}

MONGO_URI = "mongodb://localhost:27017" if not "MONGO_URI" in os.environ or os.environ[
    "MONGO_URI"] is None else os.environ["MONGO_URI"]
MONGO_DATABASE = "hacg"
