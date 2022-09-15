import os
import time

import schedule


def actress():
    os.system("scrapy crawl actress")


# run once at startup
actress()

# set schedule and run pending
schedule.every().monday.at("04:00").do(actress)

while True:
    schedule.run_pending()
    time.sleep(1)
