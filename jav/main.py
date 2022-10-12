import os
import time

import schedule


def actress():
    os.system("scrapy crawl actress")


def portfolio():
    os.system("scrapy crawl portfolio")


def onStartup():
    actress()
    portfolio()


onStartup()

# set schedule and run pending
schedule.every().monday.at("04:00").do(actress)  # 每周更新一次女优名单
schedule.every().days.at("03:00").do(portfolio)  # 每天更新一次作品集

while True:
    schedule.run_pending()
    time.sleep(1)
