import scrapy
from scrapy.selector import Selector
from loguru import logger
import sqlite3
import re


class MagnetSpider(scrapy.Spider):
    name = 'magnet'
    actor_like = None
    actor = None
    url = 'https://javdb.com'
    conn = sqlite3.connect('jav.db')

    def __init__(self, actor=None, **kwargs):
        self.actor_like = actor.strip().replace("'", '')
        super().__init__(**kwargs)

    def crawl(self):
        try:
            film_cur = self.conn.cursor()
            film_cur.execute(f"""
                SELECT * FROM films
                WHERE (name = '{self.actor[0]}' OR actor LIKE '%{self.actor[0]}%') AND (footage IS NULL)
            """)
        except Exception as e:
            logger.error(f'raise {e}')

        for film in film_cur.fetchall():
            logger.info(f'film {film}')
            yield scrapy.Request(url=f'{self.url}{film[1]}', callback=self.parse, meta={'uid': film[3]})

    def start_requests(self):
        if self.actor_like is None:
            logger.warning('you should specify a actor')
            return []

        c = self.conn.cursor()
        c.execute(f"SELECT * FROM actors WHERE alias LIKE '%{self.actor_like}%'")
        self.actor = c.fetchone()
        if self.actor is None:
            logger.warning(f'there is no actor name {self.actor_like}')
            return []

        logger.info(f'crawl {self.actor[0]}\' magnet')

        yield from self.crawl()

    def parse(self, response):
        uid = response.meta['uid']
        logger.info(f'parse magnet {uid}')
        if uid.upper().startswith('FC2'):
            logger.info('skip FC2')
            return
        if False:
            filename = f'magnet_{uid}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        video_info = {
            'uid': None,
            'date': None,
            'footage': None,
            'maker': None,
            'deliver': None,
            'rate': None,
            'category': None,
            'actor': None
        }
        panel_selector = response.xpath('//nav[@class="panel video-panel-info"]')
        for block in panel_selector.xpath('div'):
            label = block.xpath('strong/text()').get()
            value_selector = block.xpath('span')
            a_selector = value_selector.xpath('a')
            if a_selector:
                value = ','.join(a_selector.xpath('text()').getall())
            else:
                value = ','.join(value_selector.xpath('text()').getall())
            if label == '番號:':
                value = value + value_selector.xpath('text()').get()

            def mapping(key):
                return {
                    '番號:': 'uid',
                    '日期:': 'date',
                    '時長:': 'footage',
                    '片商:': 'maker',
                    '發行:': 'deliver',
                    '評分:': 'rate',
                    '類別:': 'category',
                    '演員:': 'actor',
                }.get(key, None)
            field = mapping(label)
            if not field is None:
                video_info[field] = value

        if not uid == video_info['uid']:
            logger.error(f'uid {uid} is not match video info {video_info[uid]}!')

        # update film info
        def wrapper(field):
            x = video_info[field]
            if x is None:
                return 'NULL'
            else :
                return f"'{x}'"
        try:
            c = self.conn.cursor()
            sql = f"""
                UPDATE films
                SET date = {wrapper('date')},
                    footage = {wrapper('footage')},
                    maker = {wrapper('maker')},
                    deliver = {wrapper('deliver')},
                    rate = {wrapper('rate')},
                    category = {wrapper('category')},
                    actor = {wrapper('actor')}
                WHERE uid = '{uid}';
            """
            # logger.info(sql)
            c.execute(sql)
            self.conn.commit()
        except Exception as e:
            logger.error(f'sql raise error {e}')
            self.conn.rollback()

        magnet_selector = response.xpath('//div[@id="magnets-content"]//td[@class="magnet-name"]')
        hrefs = magnet_selector.xpath('a/@href').getall()
        names = [x.xpath('span')[0].xpath('text()').get() for x in magnet_selector.xpath('a')]
        tags = []
        for a in magnet_selector.xpath('a').getall():
            tags.append(','.join(Selector(text=a).xpath('//span[contains(@class, "tag")]/text()').getall()))
        sizes = magnet_selector.xpath('a/span[@class="meta"]/text()').getall()
        sizes = [re.search(r'\(\s*(.*)', x.strip()).group(1) for x in sizes]
        dates = response.xpath(
            '//div[@id="magnets-content"]//td[@class="sub-column"]/span[@class="time"]/text()').getall()
        rows = [(uid, names[i], hrefs[i], tags[i], dates[i], sizes[i]) for i in range(len(hrefs))]

        # create table
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS magnets(
            uid text,
            name text,
            href text,
            tag text,
            date text,
            size text,
            PRIMARY KEY(href)
        );""")
        self.conn.commit()

        # save to sqlite3
        try:
            c = self.conn.cursor()
            c.executemany("""
                INSERT OR REPLACE INTO magnets(uid, name, href, tag, date, size) 
                VALUES (?,?,?,?,?,?);
            """, rows)
            logger.info(f'insert {c.rowcount} rows')
            self.conn.commit()
        except Exception as e:
            logger.error(f'sql raise error {e}')
            self.conn.rollback()
