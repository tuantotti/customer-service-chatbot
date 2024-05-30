from typing import AnyStr, Dict

import pandas as pd

from utils.logger import Logger

logger = Logger.get_logger()


def read_dataset(input_dir: AnyStr) -> pd.DataFrame:
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
