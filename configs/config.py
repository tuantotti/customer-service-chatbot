from pydantic import MongoDsn
from pydantic_settings import BaseSettings
from typing import Dict
import yaml
from utils.load_config import load_file


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DATABASE: str = "legal-chatbot"
    NUM_WORKER: int = 8

    class Config:
        env_file = ".env"


class LlmConfig:
    def __init__(self) -> None:
        _config = load_file("configs/llm_config.yaml")
        self.model_params = _config["model"]


class MilvusConfig:
    def __init__(self) -> None:
        _config = load_file("configs/database.yaml")
        self.milvus_params = _config["milvus"]


class EmbeddingConfig:
    def __init__(self) -> None:
        _config = load_file("configs/embedding_config.yaml")
        self.params = _config["model"]


class RetrieverConfig:
    def __init__(self) -> None:
        _config = load_file("configs/database.yaml")
        self.milvus_params = _config["milvus"]
        self.collection_params = self.milvus_params["collection"]


embedding_config = EmbeddingConfig()
llm_config = LlmConfig()
settings = Settings()
milvus_config = MilvusConfig()
retrieve_config = RetrieverConfig().collection_params
