from typing import AnyStr, List

from langchain_community.embeddings import HuggingFaceEmbeddings

from chatbot.utils import SingletonMeta
from configs.config import embedding_config


class EmbeddingModel(metaclass=SingletonMeta):
    def __init__(self) -> None:
        """init embedding model"""
        self.model = self.get_embedding_model(embedding_config)

    def get_embedding_model(self, params):
        """Get embedding model

        Args:
            params (_type_): the params of embedding model

        Returns:
            _type_: the loaded embedding model
        """
        embed_model = HuggingFaceEmbeddings(**params)

        return embed_model

    def embed_documents(self, documents: List) -> List:
        """Embedding the list of query

        Args:
            documents (List): list of query

        Returns:
            List: return the list of embedded queries
        """
        return self.model.embed_documents(documents)

    def embed_query(self, query: AnyStr) -> List:
        """Embedding a single query

        Args:
            query (AnyStr): a query

        Returns:
            List: embedding of that query
        """
        return self.model.embed_query(query)
