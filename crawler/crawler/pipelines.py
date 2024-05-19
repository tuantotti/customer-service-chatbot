import os
import re
import sys
from datetime import datetime
from typing import List

import pymongo
from itemadapter import ItemAdapter
from pymilvus import Collection, connections
from scrapy.exceptions import DropItem

from crawler.items import PromotionDetailItem
from crawler.utils import CleanText, check_spider_pipeline, generate_id


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

    @classmethod
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
        self.new_items = None
        self.db = None
        self.client = None
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
        self.new_items = {}

    def close_spider(self, spider):
        # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        spider.logger.info(f"Saved {len(self.new_items.keys())} new items")
        if self.new_items:
            self.db[self.collection_name].insert_many(
                [item for item in self.new_items.values()]
            )
        self.client.close()

    @check_spider_pipeline
    def process_item(self, item, spider):
        is_new_item = self.check_new_item(item=item)
        if is_new_item:
            # self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
            self.new_items[item.get("id")] = ItemAdapter(item).asdict()

            return item

        else:
            raise DropItem(f"{item} has already existed")

    def check_new_item(self, item) -> bool:
        id = generate_id(title=item["title"], date_range=item["date_range"], url=None)
        item = self.db[self.collection_name].find_one(
            {"id": id},
            ["title", "url", "date_range"],
        )

        is_new_item = False if item else True
        return is_new_item


class SyntheticDataPipeline:
    def __init__(
        self,
        llm,
        embedding_model,
        milvus_uri,
        milvus_user,
        milvus_pwd,
        milvus_collection,
    ):
        self.db = None
        self.llm = llm
        self.embedding_model = embedding_model
        self.milvus_uri = milvus_uri
        self.milvus_user = milvus_user
        self.milvus_pwd = milvus_pwd
        self.milvus_collection = milvus_collection

    @classmethod
    def from_crawler(cls, crawler):
        sys.path.append(os.path.join(os.path.abspath("../")))
        from chatbot.chat import CustomerServiceChatbot

        chatbot = CustomerServiceChatbot()
        llm = chatbot.llm
        embedding_model = chatbot.embedding_model

        return cls(
            llm=llm,
            embedding_model=embedding_model,
            milvus_uri=crawler.settings.get("MILVUS_URI"),
            milvus_user=crawler.settings.get("MILVUS_USER"),
            milvus_pwd=crawler.settings.get("MILVUS_PASSWORD"),
            milvus_collection=crawler.settings.get("MILVUS_COLLECTION"),
        )

    def open_spider(self, spider):
        connections.connect(
            "default",
            uri=self.milvus_uri,
            user=self.milvus_user,
            password=self.milvus_pwd,
        )
        self.db = Collection(self.milvus_collection)

    def close_spider(self, spider):
        connections.disconnect("default")
        del self.llm

    @check_spider_pipeline
    def process_item(self, item, spider):
        if item:
            chunks = item.get("chunks", default=[])
            if chunks:
                spider.logger.info(
                    f"Generate question answer pairs for item with id {item.get('id')}"
                )
                question_answer_pairs = self.generate_question_answer_from_chunk(chunks)
                question_answer_pair_vectors = self.embedding_model.embed_documents(
                    question_answer_pairs
                )
                self.save(question_answer_pair_vectors)
            else:
                raise DropItem(f"This item with id {item} do not have chunks")

            return item
        else:
            raise DropItem(f"This item with id {item} do not have chunks")

    def generate_question_answer_from_chunk(self, chunks: List) -> List:
        return []

    def save(self, question_answer_pairs: List):
        ids = []
        if question_answer_pairs:
            pass
        return ids
