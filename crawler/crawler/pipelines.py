import pymongo
from crawler.utils import CleanText, check_spider_pipeline
from itemadapter import ItemAdapter


class CleanDocumentPipeline:
    def __init__(self, clean_text: CleanText):
        self.clean_text = clean_text

    @classmethod
    def from_crawler(cls, crawler):
        return cls(clean_text=CleanText())

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
