import uuid
from typing import Any, AnyStr, List, Optional

from bs4 import BeautifulSoup
from scrapy import Request, Spider, signals
from scrapy.selector import Selector
from tqdm import tqdm

from crawler.items import PromotionDetailItem, PromotionItem
from crawler.pipelines import MongoPipeline, SyntheticDataPipeline
from crawler.utils import generate_id


class PromotionSpider(Spider):
    name = "promotion_crawler"

    def __init__(
        self,
        start_urls: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initial spider object

        Args:
            name (Optional[str], optional): name of spider. Defaults to None.
        """
        super().__init__(name, **kwargs)
        self.start_urls = start_urls.split(",")
        self.logger.info(self.start_urls)
        self.pipeline = {MongoPipeline, SyntheticDataPipeline}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PromotionSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        # https://stackoverflow.com/questions/28169756
        request_size = len(self.crawler.engine.slot.scheduler)
        # if 1st run, initial request_size is 0. if resumed, it is remaining requests.
        self.max_request_size = request_size

        self.pbar = tqdm()  # initialize progress bar
        self.pbar.clear()
        self.pbar.write("Opening {} spider".format(spider.name))

    def spider_closed(self, spider):
        self.pbar.clear()
        self.pbar.write("Closing {} spider".format(spider.name))
        self.pbar.close()  # close progress bar

    def parse(self, response, **kwargs):
        base_url = "https://vnptpay.vn/web/"
        promotion_selector = Selector(response).css("div#promotion div.items")
        self.pbar.total = len(promotion_selector)

        for promotion_item in promotion_selector:
            item = PromotionItem()

            item["title"] = promotion_item.css("div.group h5::text").get()
            item["date_range"] = promotion_item.css("div.group span::text").get()
            url = promotion_item.css("div.group a::attr(href)").get()

            if not (url.startswith("https://")) and not (url.startswith("http://")):
                url = base_url + url

            item["url"] = url
            self.pbar.update()
            yield Request(url, callback=self.parse_detail, dont_filter=False)

    def parse_detail(self, response):
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
        title = promotion_selector.css("h3::text").get()
        detail_item["title"] = title if title else ""
        date_range = promotion_selector.css("span::text").get()
        detail_item["date_range"] = date_range if date_range else ""
        content = self.extract_text(promotion_selector)
        detail_item["content"] = content
        detail_item["chunks"] = self.extract_chunk(promotion_selector)
        url = response.request.url
        detail_item["url"] = url if url else ""

        detail_item["id"] = generate_id(title, date_range, None)

        return detail_item

    @classmethod
    def extract_text(cls, selector: Selector) -> AnyStr:
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
            soup = BeautifulSoup(promotion_container_html, "html.parser")
            clean_text = soup.get_text(separator="\n", strip=True).strip()
            result += clean_text + " "

        return result

    @classmethod
    def extract_chunk(cls, selector: Selector) -> List:
        chunks = []
        html = selector.css("p.marginbottom-35").get()
        if not html:
            return chunks

        bs = BeautifulSoup(html, "html.parser")
        if not bs:
            return chunks

        if bs.is_empty_element:
            return chunks

        # Find all b tags
        b_tags = bs.find_all("b")

        if len(b_tags) > 0:
            for i in range(len(b_tags)):
                if i < len(b_tags) - 1:
                    start = b_tags[i]
                    end = b_tags[i + 1]
                else:
                    start = b_tags[i]
                    end = None

                content_txt = ""

                # traverse to all element between two tags
                while start != end and start is not None:
                    if start:
                        # content_txt += str(start).strip()
                        content_txt += (
                            start.getText(separator="\n", strip=True).strip() + "\n"
                        )
                        start = start.next_sibling

                chunks.append(content_txt)

        return chunks
