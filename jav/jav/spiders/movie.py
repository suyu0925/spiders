import scrapy
from pathlib import Path
from urllib.parse import urlparse
import psycopg2

from loguru import logger

class MovieSpider(scrapy.Spider):
    name = 'movie'
    url = "https://www.javbus.com/"
    conn = None
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

        movie_selector = response.xpath('//div[@class="container"]/div[@class="row movie"]')
        movie_item = MovieItem(
            avno="SSIS-477",
            date="2022-08-05",
            footage="160分鐘",
            title="三上悠亜 10変化 極上オナニーサポート",
            director="TAKE-D",
            maker="エスワン ナンバーワンスタイル",
            publisher="S1 NO.1 STYLE",
            series="10変化",
            actresses=["三上悠亜"],
            genre=["DMM獨家", "單體作品", "薄馬賽克", "乳交"],
        )
        yield movie_item
