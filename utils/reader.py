from typing import AnyStr, Dict
from utils.logger import Logger
import pandas as pd

logger = Logger.get_logger()


def read_dataset(input_dir: AnyStr) -> Dict:
    dataset = None
    try:
        if input_dir.endswith(".csv"):
            dataset = pd.read_csv(input_dir)
        elif input_dir.endswith(".json"):
            dataset = pd.read_json(input_dir)

    except Exception as e:
        logger.error(e)
        dataset = None
    
    return dataset
