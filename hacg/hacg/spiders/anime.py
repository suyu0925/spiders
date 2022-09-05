import datetime
import os
import re

import scrapy
from hacg.items import ArticleItem


class AnimeSpider(scrapy.Spider):
    name = 'anime'

    def start_requests(self):
        yield scrapy.Request("https://www.hacg.mom/wp/anime.html", self.parse)

    def parse(self, response):
        os.makedirs('tmp', exist_ok=True)
        with open("tmp/anime.html", 'wb') as f:
            f.write(response.body)

        articles_selector = response.xpath("//article")
        for article_selector in articles_selector:
            article_item = ArticleItem(
                id=article_selector.xpath(".//@id").get(),
                title=article_selector.xpath(".//header/h1/a/text()").get(),
                content=''.join([x.strip() for x in article_selector.xpath(".//div[@class='entry-content']/p/text()").extract()]),
                update_time=article_selector.xpath(
                    ".//div[@class='entry-meta']/a/time/@datetime").get(),
                href=article_selector.xpath(".//header/h1/a/@href").get(),
                magnet=None
            )
            if article_item['href'] is not None:
                yield scrapy.Request(article_item['href'], callback=self.parse_article, cb_kwargs=dict(article_item=article_item))

    def parse_article(self, response, article_item):
        os.makedirs('tmp', exist_ok=True)
        with open(f"tmp/{article_item['id']}.html", 'wb') as f:
            f.write(response.body)

        text = ''.join(response.xpath("//div[@class='entry-content']/node()").extract())
        magnet = re.search(r"[0-9a-fA-F]{40}", text)
        if magnet is not None:
            article_item['magnet'] = "magnet:?xt=urn:btih:" + magnet.group()

        yield article_item
