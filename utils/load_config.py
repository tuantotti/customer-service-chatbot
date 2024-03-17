from typing import AnyStr, Dict
import yaml
import json
from utils.logger import Logger

logger = Logger.get_logger()


def load_file(file_path: AnyStr) -> Dict:
    config = {}
    with open(file_path) as file:
        try:
            if file_path.endswith(".json"):
                config = json.load(file)
            elif file_path.endswith(".yaml"):
                config = yaml.safe_load(file)
        except Exception as e:
            logger.warn(e)

    return config
