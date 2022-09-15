# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

class JavSpiderMiddleware:
    def process_request(self, request, spider):
        request.cookies['locale'] = 'zh'


class ProxySpiderMiddleware():
    def process_request(self, request, spider):
        if spider.settings['PROXY'] is not None and not spider.settings['PROXY'] == '':
            request.meta["proxy"] = spider.settings['PROXY']
