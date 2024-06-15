from typing import AnyStr, List, Dict

import aiohttp
import pymongo
from itemadapter import ItemAdapter
from pymilvus import Collection, connections
from pyvi.ViTokenizer import tokenize
from scrapy.exceptions import DropItem

from crawler.settings import SYNTHETIC_PROMPT
from crawler.utils import (LLMAPI, CleanText, check_spider_pipeline, embedd,
                           extract_question, generate_id)


class CleanDocumentPipeline:
    """Clean document pipeline"""

    def __init__(self, clean_text: CleanText):
        self.clean_text = clean_text

    @classmethod
    def from_crawler(cls, crawler):
        return cls(clean_text=CleanText())

    @check_spider_pipeline
    def process_item(self, item, spider):
        item["content"] = self.clean_text(text=item["content"])
        item["chunks"] = [self.clean_text(text=chunk) for chunk in item["chunks"]]
        return item


class CheckDuplicatedPipeline:

    def __init__(self, mongo_uri, mongo_db):
        self.new_items = None
        self.db = None
        self.client = None
        self.collection_name = "crawled_data"
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", ""),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.new_items = {}

    def close_spider(self, spider):
        self.client.close()

    @check_spider_pipeline
    def process_item(self, item, spider):
        is_new_item = self.check_new_item(item=item)
        if is_new_item:
            self.new_items[item.get("id")] = ItemAdapter(item).asdict()

            return item

        else:
            raise DropItem(f"{item} has already existed")

    def check_new_item(self, item) -> bool:
        """check new promotion

        Args:
            item (_type_): An item from crawling

        Returns:
            bool: True if Item is existed else Item is new
        """
        _id = generate_id(title=item["title"], date_range=item["date_range"], url=None)
        item = self.db[self.collection_name].find_one(
            {"id": _id},
            ["title", "url", "date_range"],
        )

        is_new_item = False if item else True
        return is_new_item


class SyntheticDataPipeline:
    """Generate questions from a chunk pipeline"""

    def __init__(
        self,
        llm,
        milvus_uri,
        milvus_user,
        milvus_pwd,
        milvus_collection_name,
        mongo_uri,
        mongo_db,
    ):
        self.db = None
        self.milvus_uri = milvus_uri
        self.milvus_user = milvus_user
        self.milvus_pwd = milvus_pwd
        self.milvus_collection_name = milvus_collection_name
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.llm = llm

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            llm=LLMAPI(type="gemini"),
            milvus_uri=crawler.settings.get("MILVUS_URI"),
            milvus_user=crawler.settings.get("MILVUS_USER"),
            milvus_pwd=crawler.settings.get("MILVUS_PASSWORD"),
            milvus_collection_name=crawler.settings.get("MILVUS_COLLECTION"),
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", ""),
        )

    def open_spider(self, spider):
        connections.connect(
            "default",
            uri=self.milvus_uri,
            user=self.milvus_user,
            password=self.milvus_pwd,
        )
        self.milvus_collection = Collection(self.milvus_collection_name)
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.mongo_db = self.client[self.mongo_db]
        self.mongo_collection = self.mongo_db["crawled_data"]

    def close_spider(self, spider):
        connections.disconnect("default")

    @check_spider_pipeline
    async def process_item(self, item, spider):
        title = item.get("title", "")
        url = item.get("url", "")
        chunks = item.get("chunks", default=[])
        promotion_id = item.get("id", default="")

        if not chunks:
            raise DropItem(f"This item with id {promotion_id} do not have chunks")

        synthetic_data = []
        for chunk in chunks:
            prompt_str = SYNTHETIC_PROMPT.format(
                title=title, link=url, content=str(chunk)
            )

            # Generate questions
            synthetic_question = self.llm.invoke(prompt_str)

            # Convert to list of question
            questions = extract_question(synthetic_question)

            tokenize_questions = [tokenize(str(question)) for question in questions]
            # convert questions to vectors
            question_vectors = embedd(tokenize_questions)

            data = [
                {
                    "text": chunk,
                    "vector": question_vector,
                    "metadata": {
                        # "answer": question_answer["answer"],
                        "question": question,
                        "context": chunk,
                        "promotion_id": promotion_id,
                    },
                }
                for question, question_vector in zip(questions, question_vectors)
            ]

            synthetic_data.extend(data)

        try:
            self.save_milvus(synthetic_data)
            self.save_mongo(ItemAdapter(item).asdict())
            spider.logger.info(f"Save embedding and text for item with id {promotion_id}")
        except Exception as e:
            spider.logger.error(f"{e}")
            raise DropItem(f"Can not save embedding for item with id {promotion_id}")

        return item

    def save_milvus(self, data: List):
        ids = []
        try:
            ids = self.milvus_collection.insert(data=data)
            return ids
        except Exception as e:
            raise e

    def save_mongo(self, data: Dict):
        try:
            ids = self.mongo_collection.insert_one(data)

            return ids
        except Exception as e:
            raise e