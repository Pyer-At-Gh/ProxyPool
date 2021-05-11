import scrapy
from ..items import IPItem
from utils.proxy import check_proxy, check_proxy_type
from utils.common import hash_code
import logging

logger = logging.getLogger(__name__)


class KuaiSpider(scrapy.Spider):
    name = 'Kuai'
    allowed_domains = ['www.kuaidaili.com']

    def start_requests(self):
        urls = [
            'https://www.kuaidaili.com/free/inha/{}',
            'https://www.kuaidaili.com/free/intr/{}',
        ]
        for url in urls:
            for i in range(1, 4001):
                yield scrapy.Request(url=url.format(i), callback=self.parse, dont_filter=True)

    def parse(self, response):
        if response.status == 200:
            item = IPItem()
            tr_list = response.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr')
            for tr in tr_list:
                td = tr.xpath('td/text()').extract()
                item['id'] = hash_code(td[0]+':'+td[1]+'XiLa')
                item['host'] = td[0]
                item['port'] = td[1]
                item['anonymous'] = td[2]
                item['type'] = check_proxy_type(td[3])
                item['region'] = td[4]
                item['web'] = 'Kuai'
                item['valid'] = check_proxy(item['host'], item['port'], item['type'])
                yield item
        else:
            logger.info(response)