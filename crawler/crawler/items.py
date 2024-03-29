import scrapy


class PromotionItem(scrapy.Item):
    title = scrapy.Field()
    date_range = scrapy.Field()
    url = scrapy.Field()


class PromotionDetailItem(scrapy.Item):
    title = scrapy.Field()
    date_range = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
