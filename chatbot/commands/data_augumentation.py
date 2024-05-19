import datetime

import click
# from g4f.client import Client
from tqdm import tqdm

from utils.logger import Logger
from utils.reader import read_dataset

logger = Logger.get_logger()

METHOD_TYPE = {1: "Gemini_Generate_Data", 2: "GPT4_g4f_Generate_Data"}

template_question_answer_pair = """Bạn là chuyên gia về chăm sóc khác hàng. Công việc của bạn là tạo ra dữ liệu hội thoại thực tế bao gồm 20 cặp câu hỏi, câu trả lời giữa khách hàng và nhân viên chăm sóc khách hàng bằng tiếng Việt về thắc mắc của người dùng có thể có về chương trình khuyến mãi sản phẩm.Giọng điệu trong câu trả lời của nhân viên chăm sóc khác hàng phải trang trọng, ấm áp và lịch sự.Mỗi cặp câu hỏi, câu trả lời phải ngăn cách nhau bởi chuỗi "************"; giữa câu hỏi và câu trả lời ngăn cách bởi chuỗi "******".20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi, không sử dụng tên thay thế nào khác. 20 câu trả lời được tạo ra cần chèn LINK KHUYẾN MÃI nếu bạn thấy hợp lý.
Dưới đây là một ví dụ về một cặp câu hỏi, câu trả lời dựa trên chương trình khuyến mãi:
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money
LINK KHUYẾN MÃI: https://vnptpay.vn/web/khuyenmai/diennuoc0324
THÔNG TIN KHUYẾN MÃI: 
1. Thời gian triển khai:
06/3/2024 – 30/4/2024
2. Phạm vi:
Toàn quốc.
3. Đối tượng:
Khách hàng có tài khoản VNPT Money (tài khoản ví VNPT Pay định danh và liên kết ngân hàng hoặc có tài khoản Mobile Money định danh), đồng thời chưa từng thanh toán Điện hoặc Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 qua VNPT Money.

Cặp câu hỏi, câu trả lời:
************
Khách hàng: Tôi muốn tham gia chương trình khuyến mãi "Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money". Xin cho tôi biết thời gian triển khai là khi nào?
******
Nhân viên: Thưa quý khách, chương trình "Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money" được triển khai từ ngày 06/3/2024 đến ngày 30/4/2024.
************

Dựa vào ví dụ mà tôi đã cung cấp, hãy tạo ra 20 cặp câu hỏi, câu trả lời giữa người dùng và nhân viên chăm sóc khách hàng ứng với CHƯƠNG TRÌNH KHUYẾN MÃI dưới đây: 
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: {title}
LINK KHUYẾN MÃI: {link} 
THÔNG TIN KHUYẾN MÃI: "{content}" 

20 cặp câu hỏi, câu trả lời:
"""

template_question_answer_context_triplet = """Bạn là chuyên gia về chăm sóc khác hàng. Công việc của bạn là tạo ra dữ liệu hội thoại thực tế bao gồm 20 cặp câu hỏi, câu trả lời và thông tin tham chiều trong sản phẩm để trả lời câu hỏi giữa khách hàng và nhân viên chăm sóc khách hàng bằng tiếng Việt về thắc mắc của người dùng có thể có về chương trình khuyến mãi sản phẩm.Giọng điệu trong câu trả lời của nhân viên chăm sóc khác hàng phải trang trọng, ấm áp và lịch sự.Mỗi cặp câu hỏi, câu trả lời phải ngăn cách nhau bởi chuỗi "************"; giữa câu hỏi, câu trả lời và thông tin tham chiếu ngăn cách bởi chuỗi "******". 20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi, không sử dụng tên thay thế nào khác. Giọng điệu trong câu trả lời của nhân viên phải ấm áp, tử tế và lịch sự.
Dưới đây là một ví dụ về một cặp câu hỏi, câu trả lời dựa trên chương trình khuyến mãi:
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money
LINK KHUYẾN MÃI: https://vnptpay.vn/web/khuyenmai/diennuoc0324
THÔNG TIN KHUYẾN MÃI: 
1. Thời gian triển khai: 06/3/2024 – 30/4/2024
2. Phạm vi:
Toàn quốc.
3. Đối tượng:
Khách hàng có tài khoản VNPT Money (tài khoản ví VNPT Pay định danh và liên kết ngân hàng hoặc có tài khoản Mobile Money định danh), đồng thời chưa từng thanh toán Điện hoặc Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 qua VNPT Money.

Cặp câu hỏi, câu trả lời:
************
Khách hàng: Tôi muốn tham gia chương trình khuyến mãi "Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money". Xin cho tôi biết thời gian triển khai là khi nào?
******
Nhân viên: Thưa quý khách, chương trình "Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money" được triển khai từ ngày 06/3/2024 đến ngày 30/4/2024.
******
Thông tin tham chiếu: Thời gian triển khai: 06/3/2024 – 30/4/2024
************

Hãy tạo ra 20 cặp câu hỏi, câu trả lời giữa người dùng và nhân viên chăm sóc khách hàng ứng với CHƯƠNG TRÌNH KHUYẾN MÃI dưới đây: 
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: {title}
LINK KHUYẾN MÃI: {link} 
THÔNG TIN KHUYẾN MÃI: "{content}" 

20 cặp câu hỏi, câu trả lời, thông tin tham chiếu để trả lời câu hỏi:
"""

TEMPLATE_TYPE = {
    1: template_question_answer_pair,
    2: template_question_answer_context_triplet,
}


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
@click.option(
    "--api_key",
    "-ak",
    default="",
    help="",
)
@click.option(
    "--template_type",
    "-tmp",
    default=1,
    help="",
)
def run(
    input_dir: str = None,
    method_type: int = 1,
    api_key: str = None,
    template_type: int = 1,
) -> None:
    output_dir = "output/response/"
    # client = Client()
    dataset = read_dataset(input_dir=input_dir)
    # dataset = dataset.iloc[:10, :]

    template = TEMPLATE_TYPE[template_type]
    if dataset is not None:
        if method_type == 1:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")

            for i in tqdm(range(len(dataset))):
                title = dataset.loc[i, "title"]
                link = dataset.loc[i, "url"]
                content = dataset.loc[i, "content"]

                if title and content:
                    prompt = template.format(title=title, link=link, content=content)

                    dataset.loc[i, "prompt"] = prompt
                    try:
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                candidate_count=1
                            ),
                        )

                        dataset.loc[i, "chat"] = response.text
                    except Exception as e:
                        logger.warning(e)
                        dataset.loc[i, "prompt"] = ""
                        dataset.loc[i, "chat"] = ""

                else:
                    dataset.loc[i, "prompt"] = ""
                    dataset.loc[i, "chat"] = ""

    now = datetime.datetime.now()
    current_time_ft = now.strftime("%Y_%m_%d_%H_%M")
    file_name = f"llm_{current_time_ft}.csv"
    output_path = f"{output_dir}{METHOD_TYPE[method_type]}_{file_name}"
    dataset.to_csv(output_path, index=False)
    logger.info(f"Save prompts in {output_path}")


if __name__ == "__main__":
    run()
