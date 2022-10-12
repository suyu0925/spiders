# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item


class ActressItem(Item):
    name = Field()              # 日文名
    former_names = Field()      # 曾用名，为数组
    chinese_name = Field()      # 中文名
    avatar = Field()            # 头像网址
    javbus_href = Field()       # javbus站的演员网址
    uncensored = Field()        # 是否下马
    rank = Field()              # 排名

class PortfolioItem(Item):
    actress = Field()           # 演员
    avno = Field()              # 番号
    name = Field()              # 影片名
    date = Field()              # 日期
    javbus_href = Field()       # javbus站的影片网址
    javbus_tags = Field()       # javbus站的影片标签
