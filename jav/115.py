import sqlite3
import sys
from loguru import logger

if __name__ == '__main__':
    logger.info(f'argv: {sys.argv}')
    if len(sys.argv) < 2:
        logger.error('usage: python3 115.py 逢見リカ [2020-04-19]')
    actor_arg = sys.argv[1]
    date_arg = sys.argv[2] if len(sys.argv) > 2 else None

    conn = sqlite3.connect('jav.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM actors WHERE alias LIKE '%{actor_arg}%'")
    actor = c.fetchone()
    if actor is None:
        logger.warning(f'there is not actor {actor_arg}')
    logger.info(f'actor: {actor}')

    data_clause = f'AND date > {date_arg}' if date_arg else ''
    c.execute(f"SELECT uid FROM films WHERE actor LIKE '%{actor[0]}%' {data_clause} ORDER BY date DESC")
    films = c.fetchall()
    logger.info(f'films: {films}')

    magnets = []
    for film in films:
        tags_priority = [
            '高清,字幕,優',
            '高清,字幕',
            '高清',
            ''
        ]
        magnet = None
        for tags in tags_priority:
            tag_clause = ' '.join([f"AND tag like '%{x}%'" for x in tags.split(',')])
            c.execute(f"SELECT href FROM magnets WHERE uid = '{film[0]}' {tag_clause}")
            magnet = c.fetchone()
            if magnet:
                magnets.append(magnet[0])
                break
        if magnet is None:
            logger.info(f'not found magnet for {film[0]}')
    
    with open('output.txt', 'w', encoding="utf-8") as f:
        for magnet in magnets:
            f.write(magnet + '\n')
        logger.info(f"output {actor_arg} {date_arg if date_arg else ''} done")
