import scrapy
from ..items import IPItem
from utils.proxy import check_proxy, check_proxy_type
from utils.common import hash_code


class XilaSpider(scrapy.Spider):
    name = 'XiLa'
    allowed_domains = ['www.xiladaili.com']

    def start_requests(self):
        urls = [
            'http://www.xiladaili.com/putong/{}/',
            'http://www.xiladaili.com/gaoni/{}/',
            'http://www.xiladaili.com/http/{}/',
            'http://www.xiladaili.com/https/{}/'
        ]
        for url in urls:
            for i in range(1, 2):
                yield scrapy.Request(url=url.format(i), callback=self.parse, dont_filter=True)

    def parse(self, response):
        if response.status == 200:
            item = IPItem()
            tr_list = response.xpath('//*[@class="fl-table"]/tbody/tr')
            for tr in tr_list:
                td = tr.xpath('td/text()').extract()
                ip = td[0]
                item['id'] = hash_code(ip+'XiLa')
                item['host'] = ip.split(':')[0]
                item['port'] = ip.split(':')[1]
                item['type'] = check_proxy_type(td[1])
                item['anonymous'] = td[2]
                item['region'] = td[3]
                item['web'] = 'XiLa'
                item['valid'] = check_proxy(item['host'], item['port'], item['type'])
                yield item
        else:
            print(response.status)




