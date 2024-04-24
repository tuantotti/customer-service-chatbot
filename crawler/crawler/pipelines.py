import re
from datetime import datetime
from typing import List

import pymongo
from crawler.items import PromotionDetailItem
from crawler.utils import CleanText, check_spider_pipeline
from itemadapter import ItemAdapter


class CleanDocumentPipeline:
    def __init__(self, clean_text: CleanText):
        self.clean_text = clean_text

    @classmethod
    def from_crawler(cls, crawler):
        return cls(clean_text=CleanText())

    def check_expire_item(self, item: PromotionDetailItem) -> bool:
        """check whether a promotion item is expire or not expire

        Args:
            item (PromotionDetailItem): a promotion item

        Returns:
            bool: True if a promotion is expire otherwise False
        """
        date_pattern = r"[0-9]+/[0-9]+/[0-9]+"
        extract_date = re.findall(date_pattern, item["date_range"])

        return self.is_expire_date(extract_date)

    def is_expire_date(self, extract_date: List) -> bool:
        """Check a date or a range of date is expire or not expire compared to current date

        Args:
            extract_date (List): list of date ([from_date, end_date] or [from_date] or [])

        Returns:
            bool: True if date is expire, otherwise return False
        """
        from_date, end_date = "", ""
        is_expire = False
        if len(extract_date) == 1:
            from_date = extract_date[0]

        if len(extract_date) == 2:
            from_date = extract_date[0]
            end_date = extract_date[1]

        today = datetime.today()
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
            is_expire = from_date < today < end_date_obj
        elif from_date:
            is_expire = from_date < today
        else:
            is_expire = False

        return is_expire

    @check_spider_pipeline
    def process_item(self, item, spider):
        item["content"] = self.clean_text(text=item["content"])
        return item


class MongoPipeline:
    collection_name = "crawled-data"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
