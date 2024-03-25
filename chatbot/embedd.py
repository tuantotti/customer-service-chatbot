from typing import AnyStr, List

from langchain_community.embeddings import HuggingFaceEmbeddings

from configs.config import embedding_config


class EmbeddingModel:
    def __init__(self) -> None:
        self.model = self.get_embedding_model(embedding_config)

    def get_embedding_model(self, params):
        embed_model = HuggingFaceEmbeddings(**params)

        return embed_model

    def embed_documents(self, documents: List) -> List:
        return self.model.embed_documents(documents)

    def embed_query(self, query: AnyStr) -> List:
        return self.model.embed_query(query)
