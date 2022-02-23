import datetime
import os

import scrapy
from sshs.items import ArticleItem


class MonthlyCollectionSpider(scrapy.Spider):
    name = 'monthly_collection'

    def start_requests(self):
        yield scrapy.Request("https://www.sshs.xyz/category/%E5%90%8D%E7%95%AA%E5%8A%A8%E7%94%BB.html", self.parse)

    def parse(self, response):
        os.makedirs('tmp', exist_ok=True)
        with open("tmp/字幕组名番.html", 'wb') as f:
            f.write(response.body)

        articles_selector = response.xpath("//article[@class='excerpt']")
        for article_selector in articles_selector:
            article_item = ArticleItem(
                title=article_selector.xpath(".//header/h2/a/text()").get(),
                update_time=article_selector.xpath(
                    ".//p/time/text()").getall()[1],
                href=article_selector.xpath(".//header/h2/a/@href").get(),
            )
            yield scrapy.Request(article_item['href'], callback=self.parse_article, cb_kwargs=dict(article_item=article_item))

    def parse_article(self, response, article_item):
        os.makedirs('tmp', exist_ok=True)
        with open(f"tmp/{article_item['title']}.html", 'wb') as f:
            f.write(response.body)

        article_item['magnet'] = response.xpath(
            "//div[@class='dl-item']/a[normalize-space(text())='磁力']/@href").get()

        yield article_item
