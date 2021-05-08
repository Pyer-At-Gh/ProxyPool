# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IPItem(scrapy.Item):
    id = scrapy.Field()
    host = scrapy.Field()
    port = scrapy.Field()
    web = scrapy.Field()
    type = scrapy.Field()
    anonymous = scrapy.Field()
    region = scrapy.Field()
    valid = scrapy.Field()




