import scrapy

class MovieSpider(scrapy.Spider):
    name = 'movie'
    conn = None

    def __init__(self, head=50, *args, **kwargs):
        self.head = head
        super().__init__(*args, **kwargs)

    def start_requests(self):
        print(f"PG_URI: {self.settings.get('PG_URI')}")
        # yield scrapy.Request(url=self.url, callback=self.parse)
        yield None

    def parse(self, response):
        pass
