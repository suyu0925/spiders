from itemloaders.processors import TakeFirst
from scrapy.item import Field, Item


class ArticleItem(Item):
    title = Field()
    update_time = Field()
    href = Field()
    magnet = Field()
