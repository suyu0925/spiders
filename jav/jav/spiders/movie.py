import scrapy
from pathlib import Path
from urllib.parse import urlparse
import psycopg2

from loguru import logger
from jav.items import MovieItem
from scrapy import Selector

class MovieSpider(scrapy.Spider):
    name = 'movie'
    url = "https://www.javbus.com/"
    avno = None

    def __init__(self, avno='SSIS-477', *args, **kwargs):
        self.avno = avno
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.url + self.avno, callback=self.parse)

    def parse(self, response):
        if self.settings.getbool("SAVE_HTML"):
            path = "./downloads"
            Path(path).mkdir(parents=True, exist_ok=True)
            filename = f'{path}/movie-{self.avno}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        # gid
        javbus_gid = response.xpath('//script/text()').re(r'var gid = (\d+);')[0]

        _movie = response.xpath('//div[@class="container"]/div[@class="row movie"]')
        _screencap = _movie.xpath('.//div[contains(@class, "screencap")]')
        _info = _movie.xpath('.//div[contains(@class, "info")]')
        meta = {}
        # 影片基本信息
        for _line in _info.xpath('.//p[not(contains(@class, "star-show"))]'):
            if _line.xpath('./span[@class="header"]'):
                nodes = _line.xpath('./node()').getall()
                nodes = [x for x in nodes if not x.strip() == ""]
                nodes = [Selector(text=x).xpath('//text()').get() for x in nodes]
                [field, value] = nodes
                field = field.strip().strip(':')
                value = value.strip()
                meta[field] = value
        # TODO: 演员表
        _star_show = _info.xpath('.//p[contains(@class, "star-show")]')

        movie_item = MovieItem(
            avno=_movie.xpath('.//div[contains(class, "info")]/a/@title').get(),
            date=meta["發行日期"],
            footage=meta["長度"],
            title=_screencap.xpath('.//img/@title').get(),
            cover=self.url + _screencap.xpath('.//img/@src').get(),
            director=meta["導演"],
            maker=meta["製作商"],
            publisher=meta["發行商"],
            series=meta["系列"],
            actresses=["三上悠亜"],
            genres=["DMM獨家", "單體作品", "薄馬賽克", "乳交"],
        )
        yield movie_item
