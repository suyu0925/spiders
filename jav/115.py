import sys
from loguru import logger
import re
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin
import os

load_dotenv()

result = urlparse(os.environ['PG_URI'])
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = 5432 if result.port is None else result.port
conn = psycopg2.connect(
    database=database,
    user=username,
    password=password,
    host=hostname,
    port=port,
)

if __name__ == '__main__':
    logger.info(f'argv: {sys.argv}')
    if len(sys.argv) < 2:
        logger.error('usage: python 115.py 三上 [2022-04-19]')
    keyword_arg = sys.argv[1]
    date_arg = sys.argv[2] if len(sys.argv) > 2 else None

    c = conn.cursor()
    if len(sys.argv) == 2 and re.search(r'\w+-\d+', keyword_arg):
        # 番号
        avno = keyword_arg
        logger.info(f'番号: {avno}')
        sql_query = f"SELECT avno FROM movie WHERE avno LIKE '%{avno}%'"
        c.execute(sql_query)
        avnos = [x[0] for x in c.fetchall()]
    else:
        # 女优名字
        actress_name = keyword_arg
        logger.info(f'女优名字: {actress_name}')
        date_clause = f"AND date > '{date_arg}'" if date_arg else ''
        sql_query = f"""
            SELECT movie.avno 
            FROM movie, unnest(actresses) AS actress_name
            WHERE 
                actress_name LIKE '%{actress_name}%'
                {date_clause} 
            ORDER BY date ASC
        """
        c.execute(sql_query)
        avnos = [x[0] for x in c.fetchall()]
    c.close()
    logger.info(f'avnos: {avnos}')

    magnets = []
    if len(avnos) > 0:
        c = conn.cursor()
        for avno in avnos:
            tags_priority = [
                '高清,字幕',
                '字幕',
                '高清',
                # ''
            ]
            for tag in tags_priority:
                c.execute(f"""
                    SELECT link FROM magnet
                    WHERE avno = %s AND tags @> %s
                """, [avno, tag.split(',')])
                row = c.fetchone()
                if row:
                    magnets.append(row[0])
        c.close()

    with open('output.txt', 'w', encoding="utf-8") as f:
        for magnet in magnets:
            f.write(magnet + '\n')
        logger.info(f"output {keyword_arg} {date_arg if date_arg else ''} done")
