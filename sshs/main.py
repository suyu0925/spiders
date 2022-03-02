import os
import time

import schedule
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sshs.spiders.monthly_collection import MonthlyCollectionSpider


def job():
    # process = CrawlerProcess(get_project_settings())
    # process.crawl(MonthlyCollectionSpider)
    # process.start()
    os.system("scrapy crawl monthly_collection")

# run once at startup
job()

# set schedule and run pending
schedule.every().day.at("18:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
