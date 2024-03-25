from typing import List

from langchain.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import format_document

from configs.config import milvus_config


class VectorStore:
    def __init__(self, embedding_model) -> None:
        self.DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
            template="{page_content}"
        )
        self.vector_db = Milvus(
            embedding_function=embedding_model,
            connection_args=milvus_config.connection_args,
            **milvus_config.collection_args
        )

    def get_retriever(self):
        return self.vector_db.as_retriever(
            search_type="similarity", search_kwargs={"metric_type": "COSINE", "k": 2}
        )

    def similarity_search(self, query, limit) -> List:
        return self.retriever_model.similarity_search(query, k=limit)

    def _combine_documents(self, docs, document_separator="\n\n"):
        doc_strings = [
            format_document(doc, self.DEFAULT_DOCUMENT_PROMPT) for doc in docs
        ]
        return document_separator.join(doc_strings)
