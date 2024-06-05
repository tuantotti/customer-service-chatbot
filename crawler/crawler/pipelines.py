from typing import AnyStr, List
import aiohttp
import pymongo
from itemadapter import ItemAdapter
from pymilvus import Collection, connections
from pyvi.ViTokenizer import tokenize
from scrapy.exceptions import DropItem
from crawler.utils import (CleanText, check_spider_pipeline,
                           extract_question_answer, generate_id)
class CleanDocumentPipeline:
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
        _id = generate_id(title=item["title"], date_range=item["date_range"], url=None)
        item = self.db[self.collection_name].find_one(
            {"id": _id},
            ["title", "url", "date_range"],
        )

        is_new_item = False if item else True
        return is_new_item


_template = """Bạn là chuyên gia về chăm sóc khác hàng. Công việc của bạn là tạo ra dữ liệu câu hỏi thực tế của khách hàng bằng tiếng Việt về chương trình khuyến mãi sản phẩm. Giọng điệu trong câu trả lời của nhân viên chăm sóc khác hàng phải trang trọng, ấm áp và lịch sự. Mỗi cặp câu hỏi, câu trả lời phải ngăn cách nhau bởi chuỗi "************"; giữa câu hỏi và câu trả lời ngăn cách bởi chuỗi "******".20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi, không sử dụng tên thay thế nào khác. Các câu trả lời được tạo ra cần chèn LINK KHUYẾN MÃI nếu bạn thấy hợp lý.
Dưới đây là một ví dụ về các câu hỏi dựa trên chương trình khuyến mãi:
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money
LINK KHUYẾN MÃI: https://vnptpay.vn/web/khuyenmai/diennuoc0324
THÔNG TIN KHUYẾN MÃI: 
1. Thời gian triển khai:
06/3/2024 – 30/4/2024
2. Phạm vi:
Toàn quốc.
3. Đối tượng:
Khách hàng có tài khoản VNPT Money (tài khoản ví VNPT Pay định danh và liên kết ngân hàng hoặc có tài khoản Mobile Money định danh), đồng thời chưa từng thanh toán Điện hoặc Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 qua VNPT Money.

Các câu hỏi:
************
Khách hàng: Tôi muốn tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money. Xin cho tôi biết thời gian triển khai là khi nào?
******
Khách hàng: Chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money áp dụng ở phạm vi nào?
******
Khách hàng: Đối tượng nào được tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money?
******
Khách hàng cần có điều kiện gì để tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money?
************

Dựa vào ví dụ mà tôi đã cung cấp, hãy tạo ra ít nhất một cặp câu hỏi, câu trả lời giữa người dùng và nhân viên chăm sóc khách hàng ứng với CHƯƠNG TRÌNH KHUYẾN MÃI dưới đây: 
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: {title}
LINK KHUYẾN MÃI: {link} 
THÔNG TIN KHUYẾN MÃI: "{content}" 

Các câu hỏi:
"""


class SyntheticDataPipeline:
    def __init__(
        self,
        llm_api,
        embedding_api,
        milvus_uri,
        milvus_user,
        milvus_pwd,
        milvus_collection,
    ):
        self.db = None
        self.llm_api = llm_api
        self.embedding_api = embedding_api
        self.milvus_uri = milvus_uri
        self.milvus_user = milvus_user
        self.milvus_pwd = milvus_pwd
        self.milvus_collection = milvus_collection

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            llm_api=crawler.settings.get("LLM_API"),
            embedding_api=crawler.settings.get("EMBEDDING_API"),
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
                prompt_str = _template.format(title=title, link=url, content=chunk)
                async with aiohttp.ClientSession() as session:
                    question_answer_raw = await self.generate_synthetic_data(
                        session, prompt_str
                    )
                    question_answer_pairs = extract_question_answer(
                        question_answer_raw["content"]
                    )

                    tokenize_questions = [
                        tokenize(item["question"]) for item in question_answer_pairs
                    ]
                    question_vectors = await self.embedd_text(
                        session, tokenize_questions
                    )

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

    async def generate_synthetic_data(
        self, session: aiohttp.ClientSession, _prompt: AnyStr
    ):
        async with session.post(
            url=self.llm_api, json={"question": _prompt}
        ) as response:
            response.raise_for_status()
            result = await response.json(encoding="utf-8")

            return result

    async def embedd_text(self, session: aiohttp.ClientSession, texts: List):
        async with session.post(
            url=self.embedding_api, json={"text": texts}
        ) as response:
            response.raise_for_status()
            result = await response.json(encoding="utf-8")

            return result
