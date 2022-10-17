from pathlib import Path
from urllib.parse import urlparse, urljoin

import scrapy
import psycopg2
from loguru import logger

from jav.items import MagnetItem


class MagnetSpider(scrapy.Spider):
    """
    爬取所有没拿到磁力链接的影片
    """
    name = 'magnet'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def fetch_unfilled_movie(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT avno, javbus_gid FROM movie
            WHERE NOT EXISTS (
                SELECT 1 FROM magnet
                WHERE magnet.avno = movie.avno
            )
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    def start_requests(self):
        self.connect_to_db()
        for avno, gid in self.fetch_unfilled_movie():
            yield scrapy.Request(
                url=f"https://www.javbus.com/ajax/uncledatoolsbyajax.php?gid={gid}&lang=zh&uc=0", 
                headers={"Referer": "https://www.javbus.com"}, 
                callback=self.parse,
                cb_kwargs=dict(avno=avno)
            )

    def parse(self, response, avno):
        if self.settings.getbool("SAVE_HTML"):
            path = "./downloads"
            Path(path).mkdir(parents=True, exist_ok=True)
            filename = f'{path}/magnet-{avno}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        _magnets = response.xpath('//tr')
        for _magnet in _magnets:
            _title = _magnet.xpath('./td[1]')
            texts = _title.xpath('.//a/text()').getall()
            if len(texts) == 0:
                continue
            magnet_item = MagnetItem(
                avno = avno,
                link = _title.xpath('./a/@href').get().strip(),
                title = texts[0].strip(),
                size =  _magnet.xpath('./td[2]/a/text()').get().strip(),
                date =  _magnet.xpath('./td[3]/a/text()').get().strip(),
                tags = [x.strip() for x in texts[1:]],
            )
            # fix date
            if magnet_item['date'] == "0000-00-00":
                magnet_item['date'] = "1900-01-01"            
            yield magnet_item
