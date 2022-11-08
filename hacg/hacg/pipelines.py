import json
from urllib.parse import urlparse

import psycopg2
from itemadapter import ItemAdapter
from hacg.items import ArticleItem


class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('tmp/articles.jl', 'a', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        line = json.dumps(adapter.asdict(), default=str,
                          ensure_ascii=False) + '\n'
        self.file.write(line)
        return item


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
            CREATE TABLE IF NOT EXISTS article(
                id              text        NOT NULL,
                title           text        NOT NULL,
                content         text        NOT NULL,
                update_time     timestamp   NOT NULL,
                href            text        NOT NULL,
                magnet          text        NOT NULL,
                CONSTRAINT article_pk PRIMARY KEY (id)
            );
            CREATE INDEX IF NOT EXISTS article_update_time_index ON article (update_time);
        """)
        cur.close()
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            cur = self.conn.cursor()
            if isinstance(item, ArticleItem):
                cur.execute(f"""
                    INSERT INTO article(id, title, content, update_time, href, magnet)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT
                        ON CONSTRAINT article_pk
                        DO UPDATE SET
                            title = %s,
                            content = %s,
                            update_time = %s,
                            href = %s,
                            magnet = %s
                    ;
                """, (
                    item["id"], item["title"], item["content"], item["update_time"], item["href"], item["magnet"],
                    item["title"], item["content"], item["update_time"], item["href"], item["magnet"],
                ))
        except psycopg2.Error as e:
            print(f"psycopg2 raise error {e}")
            self.conn.rollback()
        else:
            cur.close()
            self.conn.commit()
        return item
