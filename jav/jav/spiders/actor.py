import scrapy
from loguru import logger
import re
import sqlite3


class ActorSpider(scrapy.Spider):
    name = "actor"
    url = 'https://javdb.com/actors'
    page = 1
    cat = None
    conn = sqlite3.connect('jav.db')

    def crawl(self):
        yield scrapy.Request(url=self.url + f'/?page={self.page}', callback=self.parse)

    def start_requests(self):
        try:
            c = self.conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS actors(
                name text primary key,
                alias text,
                href text,
                avatar text
            );""")
        except:
            self.conn.rollback()

        yield from self.crawl()

    def parse(self, response):
        logger.info(f'parse actor page {self.page}')
        if False:
            filename = f'actors_{self.page}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        aliases = response.selector.xpath('//div[@id="actors"]/div/a/@title').getall()
        hrefs = response.selector.xpath('//div[@id="actors"]/div/a/@href').getall()
        names = response.selector.xpath('//div[@id="actors"]/div/a/strong/text()').getall()
        names = [x.strip() for x in names]
        avatars = response.selector.xpath('//div[@id="actors"]//figure/span[@class="avatar"]/@style').getall()
        avatars = [re.search(r"url\((.*)\)", x).group(1) for x in avatars]
        rows = [(names[i], aliases[i], hrefs[i], avatars[i]) for i in range(len(names))]

        # save to sqlite3
        try:
            c = self.conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS actors(
                name text primary key,
                alias text,
                href text,
                avatar text
            );""")
            c.executemany("""INSERT OR REPLACE INTO actors VALUES (?,?,?,?);""", rows)
            logger.info(f'insert {c.rowcount} rows')
            self.conn.commit()
        except Exception as e:
            logger.error(f'sql raise error {e}')
            self.conn.rollback()

        # check if there is next page
        has_next_page = response.selector.xpath('//nav[@class="pagination"]/a[@rel="next"]/@href').get()
        if has_next_page is None:
            return

        # crawl next page
        self.page = self.page + 1
        yield from self.crawl()
