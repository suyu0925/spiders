BOT_NAME = "sshs"

SPIDER_MODULES = ['sshs.spiders']
NEWSPIDER_MODULE = 'sshs.spiders'

ITEM_PIPELINES = {
    'sshs.pipelines.JsonWriterPipeline': 1,
    'sshs.pipelines.MongoPipeline': 10          # store to mongodb
}

MONGO_URI = "mongodb://localhost:27017"
MONGO_DATABASE = "sshs"
