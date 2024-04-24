import datetime

import click
import pandas as pd
from tqdm import tqdm

from chatbot.chat import CustomerServiceChatbot
from rest_api.schemas.items import QuestionItem
from utils.logger import Logger
from utils.reader import read_dataset

logger = Logger.get_logger()


@click.command()
@click.option("--input_dir", "-i", default="datasets/input.csv", help="Input file path")
@click.option(
    "--output_dir",
    "-od",
    default="output/response/response.csv",
    help="File to save output of chatbot's response",
)
def run(
    input_dir: str = None,
    output_dir: str = None,
) -> None:
    chatbot = CustomerServiceChatbot(use_retriever=True)
    dataset = read_dataset(input_dir=input_dir)

    if dataset is not None:
        responses = []
        for i in tqdm(range(len(dataset))):
            try:
                question = dataset.loc[i, "question"]
                query = QuestionItem(question=question)
                response = chatbot.invoke(query=query)
                responses.append(response)
            except Exception as e:
                logger.error(e)

        now = datetime.datetime.now()
        current_time_ft = now.strftime("%Y-%m-%d %H:%M")
        file_name = f"chatbot_{current_time_ft}.csv"
        output_path = f"{output_dir}{file_name}"
        response_df = pd.DataFrame(responses)
        response_df.to_csv(output_path, index=False)
        logger.info(f"Save chatbot'response in {output_path}")


if __name__ == "__main__":
    run()
