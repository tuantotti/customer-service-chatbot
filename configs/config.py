import yaml
from pydantic_settings import BaseSettings


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
        self.search_params = milvus_params["search_params"]


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
milvus_config = MilvusConfig()
mongo_config = MongoConfig()
telegram_config = TelegramConfig().params
