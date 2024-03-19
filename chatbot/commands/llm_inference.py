import click
from utils.logger import Logger
from chatbot.chat import CustomerServiceChatbot
import pandas as pd
from utils.reader import read_dataset
import datetime

logger = Logger.get_logger()
@click.command()
@click.option("--input_dir", "-i", default="datasets/input.csv", help="Input file path")
@click.option(
    "--output_dir",
    "-od",
    default="output/response/response.csv",
    help="File to save output of llm's response",
)
def run(
    input_dir: str = None,
    output_dir: str = None,
) -> None:
    chatbot = CustomerServiceChatbot(use_retriever=False)
    dataset = read_dataset(input_dir=input_dir)

    if dataset:
        invalid_list = []
        for i in range(len(dataset)):
            try:
                question, context = dataset.loc[i, "question"], dataset.loc[i, "context"]
                response = chatbot.invoke({"context": context, "question": question})
                dataset.loc[i, 'response'] = response.strip()
            except Exception as e:
                dataset.loc[i, 'response'] = ""
                invalid_list.append(i)
                logger.error(e)

        now = datetime.datetime.now()
        file_name = f"{now.strftime("%Y-%m-%d_%H:%M%")}.csv"
        output_path = f"{output_dir}/{file_name}"
        dataset.to_csv(output_path, index=False)
        logger.info(f"Save llm'response in {output_path}")

if __name__ == "__main__":
    run()