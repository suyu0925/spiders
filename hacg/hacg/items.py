import datetime

from itemloaders.processors import TakeFirst
from scrapy.item import Field, Item


class ArticleItem(Item):
    id = Field()
    title = Field()
    content = Field()
    update_time = Field()
    href = Field()
    magnet = Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self['update_time'], str):
            s = self['update_time']
            self['update_time'] = datetime.datetime.strptime(s[:len(s)-3] + s[len(s)-2:], '%Y-%m-%dT%H:%M:%S%z')
