from crawler.items import PromotionItem
from scrapy import Spider
from scrapy.selector import Selector


class PromotionSpider(Spider):
    name = "promotion_crawler"
    start_urls = [
        "https://vnptpay.vn/web/khuyenmai",
    ]

    def parse(self, response):
        base_url = "https://vnptpay.vn/web/"
        promotion_selector = Selector(response).css("div#promotion div.items")

        for promotion_item in promotion_selector:
            item = PromotionItem()

            item["title"] = promotion_item.css("div.group h5::text").get()
            item["date_range"] = promotion_item.css("div.group span::text").get()
            url = promotion_item.css("div.group a::attr(href)").get()

            if not (url.startswith("https://")) and not (url.startswith("http://")):
                url = base_url + url

            item["url"] = url

            yield item
