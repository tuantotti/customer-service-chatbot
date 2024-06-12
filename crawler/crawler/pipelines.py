from typing import AnyStr, List

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
        milvus_collection,
    ):
        self.db = None
        self.milvus_uri = milvus_uri
        self.milvus_user = milvus_user
        self.milvus_pwd = milvus_pwd
        self.milvus_collection = milvus_collection
        self.llm = llm

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            llm=LLMAPI(type="gemini"),
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
        self.colection = Collection(self.milvus_collection)

    def close_spider(self, spider):
        connections.disconnect("default")

    @check_spider_pipeline
    async def process_item(self, item, spider):
        title = item.get("title", "")
        url = item.get("url", "")
        chunks = item.get("chunks", default=[])
        if chunks:
            synthetic_data = []
            for chunk in chunks:
                prompt_str = SYNTHETIC_PROMPT.format(
                    title=title, link=url, content=chunk
                )

                # Generate questions
                question_answer_raw = await self.llm.ainvoke(prompt_str)
                # Convert to list of question
                question_answer_pairs = extract_question(question_answer_raw["content"])

                tokenize_questions = [
                    tokenize(item["question"]) for item in question_answer_pairs
                ]
                # convert questions to vectors
                question_vectors = embedd(tokenize_questions)

                data = [
                    {
                        "text": question_answer["question"],
                        "vector": question_vector,
                        "metadata": {
                            "answer": question_answer["answer"],
                            "context": chunk,
                            "mongo_id": item.get("id"),
                        },
                    }
                    for question_answer, question_vector in zip(
                        question_answer_pairs, question_vectors["vectors"]
                    )
                ]

                synthetic_data.extend(data)

            try:
                self.save(synthetic_data)
                spider.logger.info(
                    f"Generate question answer pairs for item with id {item.get('id')}"
                )
            except Exception as e:
                spider.logger.warning(e)
                raise DropItem(
                    f"Can not save question answer embedding for item with id {item.get('id')}"
                )

            return item
        else:
            raise DropItem(f"This item with id {item.get('id')} do not have chunks")

    def save(self, data: List):
        ids = []
        if data:
            try:
                ids = self.colection.insert(data=data)
            except Exception as e:
                raise e
        return ids
