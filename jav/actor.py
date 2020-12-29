import sqlite3

actor = ['吉良りん', '吉良りん', '/actors/w93B?t=d', 'https://jdbimgs.com/avatars/w9/w93B.jpg']

conn = sqlite3.connect('jav.db')
c = conn.cursor()
c.execute(f"""INSERT INTO actors(name, alias, href, avatar)
     VALUES (?,?,?,?);""", actor)
conn.commit()
