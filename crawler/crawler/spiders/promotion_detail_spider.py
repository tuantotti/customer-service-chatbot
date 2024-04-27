import uuid
from typing import Any, AnyStr, Optional

import pandas as pd
from bs4 import BeautifulSoup
from crawler.items import PromotionDetailItem
from crawler.pipelines import CleanDocumentPipeline, MongoPipeline
from scrapy import Spider
from scrapy.selector import Selector


class PromotionSpider(Spider):
    name = "promotion_detail_crawler"

    def __init__(self, name: Optional[str] = None, **kwargs: Any):
        """Initial spider object

        Args:
            name (Optional[str], optional): name of spider. Defaults to None.
        """
        super().__init__(name, **kwargs)
        self.start_urls = self.init_start_urls()
        self.pipeline = set([CleanDocumentPipeline, MongoPipeline])

    def init_start_urls(self):
        """Initially urls to crawl from promotion file

        Returns:
            String: list of urls
        """
        df = pd.read_csv("output/promotion.csv")
        return df["url"].tolist()

    def parse(self, response):
        """Implement parse method to process the response of each request for each start_url

        Args:
            response (Any): the response of request url

        Yields:
            _type_: object that crawl data from an url
        """
        detail_item = PromotionDetailItem()
        promotion_selector = Selector(response).css(
            "div.promotionDetail-content div.promotionDetail-container"
        )
        detail_item["id"] = str(uuid.uuid4())
        detail_item["title"] = promotion_selector.css("h3::text").get()
        detail_item["date_range"] = promotion_selector.css("span::text").get()
        detail_item["content"] = self.extract_text(promotion_selector)
        detail_item["url"] = response.request.url

        yield detail_item

    def extract_text(self, selector: Selector) -> AnyStr:
        """Extract html to text

        Args:
            selector (Selector): the html object to extract

        Returns:
            AnyStr: the text inside html tag
        """
        result = ""
        promotion_containers = selector.css("div.promotionDetail-container")

        for promotion_container in promotion_containers:
            promotion_container_html = promotion_container.get()
            soup = BeautifulSoup(promotion_container_html)
            clean_text = soup.get_text(separator="\n", strip=True).strip()
            result += clean_text + " "

        return result
