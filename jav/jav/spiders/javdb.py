import scrapy


class JavdbSpider(scrapy.Spider):
    name = "javdb"

    def start_requests(self):
        urls = [
            'https://javdb.com/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = f'javdb.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
