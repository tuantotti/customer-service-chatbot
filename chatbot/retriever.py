from typing import List

from langchain.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import format_document
from datetime import datetime
import re
from configs.config import milvus_config


class VectorStore:
    def __init__(self, embedding_model) -> None:
        """Initial the params of retriever model

        Args:
            embedding_model (_type_): the embedding model
        """
        self.DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
            template="{page_content}"
        )
        self.param = milvus_config.search_params
        self.vector_db = Milvus(
            embedding_function=embedding_model,
            connection_args=milvus_config.connection_args,
            **milvus_config.collection_args
        )

    def get_retriever(self):
        return self.vector_db.as_retriever(
            search_type="similarity", search_kwargs={"param": self.param, "k": 10}
        )

    def similarity_search(self, query, limit) -> List:
        return self.retriever_model.similarity_search(query, k=limit)

    def extract_date(self, doc) -> str:
        date_str = ""
        date_pattern = r"[0-9]+/[0-9]+/[0-9]+"
        metadata = doc.metadata
        metadata_json = metadata.get("metadata")
        if metadata_json:
          date_range = doc["date_range"]
          date_str = re.findall(date_pattern, date_range) if date_range else ""

        return date_str
    def check_old_doc(self, doc1, doc2):
        doc1_date_str = self.extract_date(doc1)
        doc2_date_str = self.extract_date(doc2)

        
    def remove_old_docs(self, docs):
        unique_docs = {}
        for doc in docs:
            metadata = doc.metadata
            metadata_json = metadata.get("metadata")
            if metadata_json:
              id = metadata_json.get('id')
              if id:
                current_doc = unique_docs[id]
                if self.check_old_doc(current_doc, doc):
                  unique_docs[id] = doc

        return unique_docs.values()

    def _combine_documents(self, docs, document_separator="\n\n"):
        doc_strings = []
        docs = self.remove_old_docs(docs)
        for doc in docs:
            metadata = doc.metadata
            metadata_json = metadata.get("metadata")
            if metadata_json:
                window_context = metadata_json.get("window_context")
                text = window_context if window_context else format_document(doc, self.DEFAULT_DOCUMENT_PROMPT)
                doc_strings.append(text)
            else:
                doc_strings.append(format_document(doc, self.DEFAULT_DOCUMENT_PROMPT))
        return document_separator.join(doc_strings)
