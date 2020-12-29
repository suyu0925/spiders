import scrapy
from loguru import logger
import sqlite3


class FilmSpider(scrapy.Spider):
    name = 'film'
    actor_like = None
    url = 'https://javdb.com'
    page = 1
    conn = sqlite3.connect('jav.db')

    def __init__(self, actor=None, **kwargs):
        self.actor_like = actor.strip().replace("'", '')
        super().__init__(**kwargs)

    def crawl(self):
        yield scrapy.Request(url=f'{self.url}{self.actor[2]}/?page={self.page}&t=d', callback=self.parse)

    def start_requests(self):
        if self.actor_like is None:
            logger.warning('you should specify a actor')
            return []

        c = self.conn.cursor()
        sql_query = f"SELECT * FROM actors WHERE alias LIKE '%{self.actor_like}%'"
        c.execute(sql_query)
        self.actor = c.fetchone()
        if self.actor is None:
            logger.warning(f'there is no actor name {self.actor_like}')
            return []

        yield from self.crawl()

    def parse(self, response):
        logger.info(f'parse film page {self.page}')
        if False:
            filename = f'film_{self.actor[0]}_{self.page}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        hrefs = response.selector.xpath('//div[@id="videos"]//div[@class="grid-item column"]/a/@href').getall()
        titles = response.selector.xpath('//div[@id="videos"]//div[@class="grid-item column"]/a/@title').getall()
        covers = response.selector.xpath(
            '//div[@id="videos"]//div[@class="grid-item column"]/a/div/img/@data-src').getall()
        uids = response.selector.xpath(
            '//div[@id="videos"]//div[@class="grid-item column"]/a/div[@class="uid"]/text()').getall()
        dates = response.selector.xpath(
            '//div[@id="videos"]//div[@class="grid-item column"]/a/div[@class="meta"]/text()').getall()
        dates = [x.strip() for x in dates]
        tags_selector = response.selector.xpath(
            '//div[@id="videos"]//div[@class="grid-item column"]/a/div[@class="tags has-addons"]')
        tags = [','.join(x.xpath('span/text()').getall()) for x in tags_selector]
        rows = [(self.actor[0], hrefs[i], titles[i], uids[i], covers[i], tags[i], dates[i]) for i in range(len(hrefs))]

        # check if reach the bound
        try:
            c = self.conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS films(
                name text,
                href text,
                title text,
                uid text,
                cover text,
                tag text,
                date text,
                footage text,
                maker text,
                deliver text,
                rate text,
                category text,
                actor text,
                PRIMARY KEY(uid)
            );""")
            sql = f"""SELECT * FROM films 
                WHERE name = '{self.actor[0]}' AND uid = '{uids[-1]}'
            ;"""
            c.execute(sql)
            film = c.fetchone()
            if not film is None:
                logger.info(f'film({self.actor[0]}, {uids[-1]}) has crawled, {film} done job')
                return
        except Exception as e:
            logger.error(f'crawl film raise {e}')
            return

        # save to sqlite3
        try:
            c = self.conn.cursor()
            c.executemany("""
                INSERT OR REPLACE INTO films(name, href, title, uid, cover, tag, date) 
                VALUES (?,?,?,?,?,?,?);
            """, rows)
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
