import os
import time

import schedule


def actress():
    os.system("scrapy crawl actress")


def movie():
    os.system("scrapy crawl movie")


def onStartup():
    actress()
    movie()


onStartup()

# set schedule and run pending
schedule.every().monday.at("04:00").do(actress)  # 每周更新一次女演员表

while True:
    schedule.run_pending()
    time.sleep(1)
