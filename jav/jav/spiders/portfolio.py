from pathlib import Path
from urllib.parse import urlparse, urljoin

import psycopg2
import scrapy
from loguru import logger

from jav.items import PortfolioItem


class PortfolioSpider(scrapy.Spider):
    name = 'portfolio'

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

    def fetch_head_star_hrefs(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT name, javbus_href FROM actress
            ORDER BY rank ASC
            LIMIT %s
        """, [self.opt_head])
        star_hrefs = cur.fetchall()
        cur.close()
        return star_hrefs

    def start_requests(self):
        self.connect_to_db()

        for star, href in self.fetch_head_star_hrefs():
            yield scrapy.Request(url=href, callback=self.parse, cb_kwargs=dict(star=star, page=1))

    def parse(self, response, star, page):
        if self.settings.getbool("SAVE_HTML"):
            path = "./downloads"
            Path(path).mkdir(parents=True, exist_ok=True)
            filename = f'{path}/star-{star}-{page}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        movies_selector = response.xpath('//a[@class="movie-box"]')
        for movie_selector in movies_selector:
            try:
                # parse portfolio
                tags = movie_selector.xpath('.//button/text()').getall()
                portfolio_item = PortfolioItem(
                    actress=star,
                    name=movie_selector.xpath(
                        './div[@class="photo-info"]/span/text()').get(),
                    avno=movie_selector.xpath('.//date/text()').getall()[0],
                    date=movie_selector.xpath('.//date/text()').getall()[1],
                    javbus_href=movie_selector.xpath('@href').get(),
                    javbus_tags=tags,
                )
                yield portfolio_item
            except Exception as e:
                print(f"parse star throw {e}")

        next_page_href = response.xpath(
            "//ul[contains(@class, 'pagination')]//a[@id='next']/@href").get()
        print("next_page_href", next_page_href)
        if next_page_href is not None:
            yield scrapy.Request(url=urljoin(response.url, next_page_href), callback=self.parse, cb_kwargs=dict(star=star, page=page + 1))
