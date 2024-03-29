from scrapy import Spider
from scrapy.selector import Selector
from crawler.items import PromotionDetailItem
import pandas as pd
from typing import AnyStr, Optional, Any
from bs4 import BeautifulSoup
from crawler.pipelines import MongoPipeline

class PromotionSpider(Spider):
    name = "promotion_detail_crawler"
    def __init__(self, name: Optional[str] = None, **kwargs: Any):
       super().__init__(name, **kwargs)
       self.start_urls = self.init_start_urls()
       self.pipeline = set([MongoPipeline])

    def init_start_urls(self):
      df = pd.read_csv("output/promotion.csv")
      return df['url'].tolist()

    def parse(self, response):
      detail_item = PromotionDetailItem()
      promotion_selector = Selector(response).css("div.promotionDetail-content div.promotionDetail-container")
      detail_item['title'] = promotion_selector.css("h3::text").get()
      detail_item['date_range'] = promotion_selector.css("span::text").get()
      detail_item['content'] = self.extract_text(promotion_selector)
      detail_item['url'] = response.request.url
      # self.logger.info(detail_item['url'])
      
      yield detail_item

    def extract_text(self, selector: Selector) -> AnyStr:
      result = ""
      promotion_containers = selector.css("div.promotionDetail-container")

      for promotion_container in promotion_containers:
        promotion_container_html = promotion_container.get()
        soup = BeautifulSoup(promotion_container_html)
        clean_text = soup.get_text().strip()
        result += clean_text + " "
        
      return result