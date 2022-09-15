# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from urllib.parse import urlparse
import psycopg2

from jav.items import ActressItem


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
                CONSTRAINT actress_pk PRIMARY KEY (name)
            );
        """)
        cur.close()
        self.conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, ActressItem):
            cur = self.conn.cursor()
            cur.execute(f"""
                INSERT INTO actress(name, former_names, chinese_name, avatar, javbus_href)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT
                    ON CONSTRAINT actress_pk
                    DO UPDATE SET
                        former_names = %s,
                        chinese_name = %s,
                        avatar = %s,
                        javbus_href = %s
                ;
            """, (
                item["name"], item["former_names"], item["chinese_name"], item["avatar"], item["javbus_href"],
                item["former_names"], item["chinese_name"], item["avatar"], item["javbus_href"],
            ))
            cur.close()
            self.conn.commit()
        return item
