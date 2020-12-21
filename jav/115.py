import sqlite3
import sys
from loguru import logger

if __name__ == '__main__':
    logger.info(f'argv: {sys.argv}')
    if len(sys.argv) < 2:
        logger.error('usage: python3 115.py 逢見リカ [2020-04-19]')
    actor_arg = sys.argv[1]
    date_arg = sys.argv[2]

    conn = sqlite3.connect('jav.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM actors WHERE alias LIKE '%{actor_arg}%'")
    actor = c.fetchone()
    if actor is None:
        logger.warning(f'there is not actor {actor_arg}')
    logger.info(f'actor: {actor}')

    c.execute(f"SELECT uid FROM films WHERE actor LIKE '%{actor[0]}%' AND date > {date_arg}")
    films = c.fetchall()
    logger.info(f'films: {films}')

    magnets = []
    for film in films:
        c.execute(f"SELECT href FROM magnets WHERE uid = '{film[0]}'")
        magnet = c.fetchone()
        if not magnet is None:
            magnets.append(magnet[0])
    
    with open('output.txt', 'w') as f:
        for magnet in magnets:
            f.write(magnet + '\n')
