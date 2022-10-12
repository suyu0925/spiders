# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from urllib.parse import urlparse

import psycopg2

from jav.items import ActressItem, MovieItem, PortfolioItem


class PgsqlPipeline:
    conn = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            pg_uri=crawler.settings.get('PG_URI')
        )

    def __init__(self, pg_uri):
        result = urlparse(pg_uri)
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
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS actress(
                name            text    NOT NULL,
                former_names    text[],
                chinese_name    text,
                avatar          text    NOT NULL,
                javbus_href     text    NOT NULL,
                uncensored      boolean NOT NULL DEFAULT false,
                rank            int,
                CONSTRAINT actress_pk PRIMARY KEY (name)
            );

            CREATE TABLE IF NOT EXISTS portfolio(
                actress         text    NOT NULL,
                avno            text    NOT NULL,
                name            text    NOT NULL,
                date            date    NOT NULL,
                javbus_href     text    NOT NULL,
                javbus_tags     text[]  NOT NULL DEFAULT '{}',
                CONSTRAINT portfolio_pk PRIMARY KEY (actress, avno)
            );

            CREATE TABLE IF NOT EXISTS movie(
                avno            text    NOT NULL,
                date            date    NOT NULL,
                footage         text    NOT NULL,
                title           text    NOT NULL,
                director        text    NOT NULL,
                maker           text    NOT NULL,
                publisher       text    NOT NULL,
                series          text    NOT NULL,
                actresses       text[]  NOT NULL,
                genres          text[]  NOT NULL DEFAULT '{}',
                uncensored      bool    NOT NULL DEFAULT false,
                CONSTRAINT movie_pk PRIMARY KEY (avno)
            );
        """)
        cur.close()
        self.conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, ActressItem):
            cur = self.conn.cursor()
            cur.execute(f"""
                INSERT INTO actress(name, former_names, chinese_name, avatar, javbus_href, rank)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT
                    ON CONSTRAINT actress_pk
                    DO UPDATE SET
                        former_names = %s,
                        chinese_name = %s,
                        avatar = %s,
                        javbus_href = %s,
                        rank = %s
                ;
            """, (
                item["name"], item["former_names"], item["chinese_name"], item["avatar"], item["javbus_href"], item["rank"],
                item["former_names"], item["chinese_name"], item["avatar"], item["javbus_href"], item["rank"]
            ))
            cur.close()
            self.conn.commit()
        elif isinstance(item, PortfolioItem):
            cur = self.conn.cursor()
            cur.execute(f"""
                INSERT INTO portfolio(actress, avno, name, date, javbus_href, javbus_tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT
                    ON CONSTRAINT portfolio_pk
                    DO UPDATE SET
                        name = %s,
                        date = %s,
                        javbus_href = %s,
                        javbus_tags = %s
                ;
            """, (
                item["actress"], item["avno"], item["name"], item["date"], item["javbus_href"], item["javbus_tags"],
                item["name"], item["date"], item["javbus_href"], item["javbus_tags"]
            ))
            cur.close()
            self.conn.commit()         
        elif isinstance(item, MovieItem):
            cur = self.conn.cursor()
            cur.execute(f"""
                INSERT INTO movie(avno, date, footage, title, director, maker, publisher, series, actresses, genres)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT
                    ON CONSTRAINT movie_pk
                    DO UPDATE SET
                        date = %s,
                        footage = %s,
                        title = %s,
                        director = %s,
                        maker = %s,
                        publisher = %s,
                        series = %s,
                        actresses = %s,
                        genres = %s,
                ;
            """, (
                item["avno"], item["date"], item["footage"], item["title"], item["director"], item["maker"], item["publisher"], item["series"], item["actresses"], item["genres"],
                item["date"], item["footage"], item["title"], item["director"], item["maker"], item["publisher"], item["series"], item["actresses"], item["genres"]
            ))
            cur.close()
            self.conn.commit()                   
        return item
