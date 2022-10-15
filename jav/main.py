import os
import time

import schedule


def actress():
    os.system("scrapy crawl actress")


def portfolio():
    os.system("scrapy crawl portfolio")


def movie():
    os.system("scrapy crawl movie")


def magnet():
    os.system("scrapy crawl magnet")


def onStartup():
    actress()
    portfolio()
    movie()
    magnet()


def daily():
    portfolio()
    movie()
    magnet()


onStartup()

# set schedule and run pending
schedule.every().monday.at("04:00").do(actress)  # 每周更新一次女优名单
schedule.every().days.at("03:00").do(daily)  # 每天更新一次排名前50的女优作品

while True:
    schedule.run_pending()
    time.sleep(1)
