import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DATABASE: str = "legal-chatbot"
    NUM_WORKER: int = 8

    class Config:
        env_file = ".env"


class LlmConfig:
    def __init__(self) -> None:
        _config = yaml.safe_load(open("configs/llm_config.yaml", "r"))
        self.model_params = _config["model"]


class MilvusConfig:
    def __init__(self) -> None:
        _config = yaml.safe_load(open("configs/database.yaml", "r"))
        milvus_params = _config["milvus"]
        self.connection_args = milvus_params["connection_args"]
        self.collection_args = milvus_params["collection_args"]


class MongoConfig:
    def __init__(self) -> None:
        _config = yaml.safe_load(open("configs/database.yaml", "r"))
        mongo_params = _config["mongodb"]
        connection_args = mongo_params["connection_args"]
        collection_args = mongo_params["collection_args"]
        self.URI = connection_args["uri"]
        self.DATABASE_NAME = collection_args["database_name"]


class EmbeddingConfig:
    def __init__(self) -> None:
        _config = yaml.safe_load(open("configs/embedding_config.yaml", "r"))
        self.params = _config["model"]


class TelegramConfig:
    def __init__(self) -> None:
        _config = yaml.safe_load(open("configs/telegram.yaml"))
        self.params = _config["telegram"]


embedding_config = EmbeddingConfig().params
llm_config = LlmConfig().model_params
settings = Settings()
milvus_config = MilvusConfig()
mongo_config = MongoConfig()
telegram_config = TelegramConfig().params
