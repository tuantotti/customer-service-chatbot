from langchain_community.embeddings import HuggingFaceEmbeddings
from configs.config import embedding_config


class EmbeddingModel:
    def __init__(self) -> None:
        self.model = self.get_embedding_model(embedding_config.params)

    def get_embedding_model(self, params):
        embed_model = HuggingFaceEmbeddings(kwargs=params)

        return embed_model
