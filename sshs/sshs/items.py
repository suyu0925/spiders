import datetime

from itemloaders.processors import TakeFirst
from scrapy.item import Field, Item


class ArticleItem(Item):
    title = Field()
    update_time = Field()
    href = Field()
    magnet = Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self['update_time'], str):
            self['update_time'] = datetime.datetime.strptime(self['update_time'], '%Y-%m-%d')
