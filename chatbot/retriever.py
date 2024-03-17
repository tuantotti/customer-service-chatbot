from langchain_community.vectorstores import Milvus
from configs.config import milvus_config
from typing import List


class Retriever:
    def __init__(self, embedding_model) -> None:
        self.retriever_model = Milvus(
            embedding_function=embedding_model,
            connection_args=milvus_config,
            collection_name="Question_Embedding",
            vector_field="question_embedding",
            primary_field="id",
            text_field="question_id",
        )

    def get_model(self):
        return self.retriever_model

    def similarity_search(self, query, limit) -> List:
        return self.retriever_model.similarity_search(query, k=limit)
