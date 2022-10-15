import scrapy
from pathlib import Path
from urllib.parse import urlparse
import psycopg2

from loguru import logger
from jav.items import MovieItem
from scrapy import Selector

class MovieSpider(scrapy.Spider):
    """
    默认爬取排名前10的女优的全部影片
    """
    name = 'movie'
    url = "https://www.javbus.com/"

    def __init__(self, head=50, *args, **kwargs):
        self.opt_head = head
        super().__init__(*args, **kwargs)

    def connect_to_db(self):
        # print(f"PG_URI: {self.settings.get('PG_URI')}")
        result = urlparse(self.settings.get('PG_URI'))
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = 5432 if result.port is None else result.port
        self.conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
        )

    def fetch_head_avno(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT avno FROM portfolio, (
                SELECT name FROM actress
                ORDER BY rank ASC
                LIMIT 10
            ) as actress
            WHERE
                portfolio.actress = actress.name
                AND NOT EXISTS (
                    SELECT 1 FROM movie 
                    WHERE movie.avno = portfolio.avno
                )
            ORDER BY date DESC
        """, [self.opt_head])
        rows = cur.fetchall()
        cur.close()
        return [x[0] for x in rows]

    def start_requests(self):
        self.connect_to_db()
        for avno in self.fetch_head_avno():
            yield scrapy.Request(url=self.url + avno, callback=self.parse, cb_kwargs=dict(avno=avno))

    def parse(self, response, avno):
        if self.settings.getbool("SAVE_HTML"):
            path = "./downloads"
            Path(path).mkdir(parents=True, exist_ok=True)
            filename = f'{path}/movie-{avno}.html'
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
                value = value.strip() if value is not None else None
                meta[field] = value
        meta["演员表"] = _info.xpath('.//li/div[contains(@class, "star-name")]/a/text()').getall()
        meta["类型"] = _info.xpath('//span[contains(@class, "genre")]/label/a/text()').getall()
        meta["樣品圖像"] = response.xpath('//a[contains(@class, "sample-box")]/@href').getall()

        movie_item = MovieItem(
            avno=meta["識別碼"],
            date=meta["發行日期"],
            footage=meta["長度"],
            title=_screencap.xpath('.//img/@title').get(),
            cover=self.url + _screencap.xpath('.//img/@src').get(),
            director=meta.get("導演"),
            maker=meta.get("製作商"),
            publisher=meta.get("發行商"),
            series=meta.get("系列"),
            actresses=meta["演员表"],
            genres=meta["类型"],
            uncensored=False,
            samples=meta["樣品圖像"],
            javbus_gid=javbus_gid,
        )
        yield movie_item
