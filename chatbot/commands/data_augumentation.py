import datetime

import click
from g4f.client import Client
from tqdm import tqdm

from rest_api.schemas.items import QuestionItem
from utils.logger import Logger
from utils.reader import read_dataset

logger = Logger.get_logger()

METHOD_TYPE = {1: "Generate_Prompt"}


@click.command()
@click.option(
    "--input_dir",
    "-i",
    default="crawler/output/promotion_detail_raw.csv",
    help="Input file path",
)
@click.option(
    "--method_type",
    "-t",
    default=1,
    help="",
)
def run(
    input_dir: str = None,
    method_type: str = None,
) -> None:
    output_dir = "output/response/"
    client = Client()
    dataset = read_dataset(input_dir=input_dir)

    template = """Công việc của bạn là tạo ra dữ liệu hội thoại thực tế bao gồm 20 cặp câu hỏi, câu trả lời giữa khách hàng và nhân viên chăm sóc khách hàng bằng tiếng Việt về thắc mắc của người dùng có thể có về chương trình khuyến mãi sản phẩm. 20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi là "{title}", không sử dụng tên thay thế nào khác. 20 câu trả lời được tạo ra cần chèn LINK KHUYẾN MÃI {link} nếu bạn thấy hợp lý. Hãy dựa trên THÔNG TIN KHUYẾN MÃI sản phẩm dưới đây hãy tạo ra 20 cặp câu hỏi, câu trả lời giữa người dùng và nhân viên chăm sóc khách hàng: \nTHÔNG TIN KHUYẾN MÃI: "{content}" """
    if dataset is not None and method_type == 1:
        for i in tqdm(range(len(dataset))):
            title = dataset.loc[i, "title"]
            link = dataset.loc[i, "url"]
            content = dataset.loc[i, "content"]
            promt_1 = f"""Tất cả 20 câu hỏi bạn tạo ra cần chứa cụm "{title}" """
            dataset.loc[i, "additional prompt"] = promt_1

            if title and content:
                prompt = template.format(title=title, link=link, content=content)

                dataset.loc[i, "prompt"] = prompt

            else:
                dataset.loc[i, "prompt"] = ""

    now = datetime.datetime.now()
    current_time_ft = now.strftime("%Y-%m-%d %H:%M")
    file_name = f"llm_{current_time_ft}.csv"
    output_path = f"{output_dir}{METHOD_TYPE[method_type]}_{file_name}"
    dataset.to_csv(output_path, index=False)
    logger.info(f"Save llm'response in {output_path}")


if __name__ == "__main__":
    run()
