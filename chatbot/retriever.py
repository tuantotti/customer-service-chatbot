from typing import List

from langchain.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Milvus
from langchain_core.prompts import format_document

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

    def _combine_documents(self, docs, document_separator="\n\n"):
        doc_strings = []
        for doc in docs:
            metadata = doc.metadata
            metadata_json = metadata.get("metadata")
            format_docs = format_document(doc, self.DEFAULT_DOCUMENT_PROMPT)
            if metadata_json:
                window_context = metadata_json.get("window_context")
                doc_strings.append(window_context if window_context else format_docs)
            else:
                doc_strings.append(format_docs)
        return document_separator.join(doc_strings)
