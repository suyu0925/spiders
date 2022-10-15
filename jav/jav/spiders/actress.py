import re
from pathlib import Path
from urllib.parse import urljoin

from jav.items import ActressItem
from loguru import logger
from scrapy import Request, Spider


class ActressSpider(Spider):
    """
    爬取所有的有码女优
    """
    name = "actress"
    url = "https://www.javbus.com/actresses"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        yield Request(url=self.url, callback=self.parse)

    def parse(self, response, page=1):
        if self.settings.getbool("SAVE_HTML"):
            path = "./downloads"
            Path(path).mkdir(parents=True, exist_ok=True)
            filename = f'{path}/actresses-{page}.html'
            with open(filename, 'wb') as f:
                f.write(response.body)
            logger.info(f'Saved file {filename}')

        items_selector = response.xpath(
            "//div[@id='waterfall']/div[@class='item']")
        for index, item_selector in enumerate(items_selector):
            try:
                # parse names
                full_name = item_selector.xpath(
                    ".//a/div[@class='photo-info']/span/text()").get()
                name = re.match("([^（）]+)[（]?", full_name).groups()[0]
                m = re.search("(?<=（)([^）]+)", full_name)
                former_names = m.groups()[0].split('、') if m is not None else None

                actress_item = ActressItem(
                    name=name,
                    former_names=former_names,
                    chinese_name=None,
                    avatar=item_selector.xpath(
                        ".//a/div[@class='photo-frame']/img/@src").get(),
                    javbus_href=item_selector.xpath(
                        ".//a/@href").get(),
                    uncensored=False,
                    rank=(page-1)*50+(index+1)
                )
                yield actress_item
            except Exception as e:
                print(f"parse actress throw {e}")

        next_page_href = response.xpath(
            "//ul[contains(@class, 'pagination')]//a[@id='next']/@href").get()
        print("next_page_href", next_page_href)
        if next_page_href is not None:
            yield Request(url=urljoin(response.url, next_page_href), callback=self.parse, cb_kwargs=dict(page=page + 1))
