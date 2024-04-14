import datetime

import pandas as pd
from g4f.client import Client
from tqdm import tqdm

from chatbot.prompts import PredefinedPrompt
from utils.logger import Logger

logger = Logger.get_logger()

client = Client()

df = pd.read_csv("crawler/output/promotion_detail.csv")
template = """Công việc của bạn là tạo ra dữ liệu hội thoại thực tế bao gồm 20 cặp câu hỏi, câu trả lời giữa khách hàng và nhân viên chăm sóc khách hàng bằng tiếng Việt về thắc mắc của người dùng có thể có về chương trình khuyến mãi sản phẩm. 20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi là "{title}", không sử dụng tên thay thế nào khác. 20 câu trả lời được tạo ra cần chèn LINK KHUYẾN MÃI {link} nếu bạn thấy hợp lý. Hãy dựa trên THÔNG TIN KHUYẾN MÃI sản phẩm dưới đây hãy tạo ra 20 cặp câu hỏi, câu trả lời giữa người dùng và nhân viên chăm sóc khách hàng: \nTHÔNG TIN KHUYẾN MÃI: "{content}" """

title = "Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money"
link = "https://vnptpay.vn/web/khuyenmai/diennuoc0324"
content = """
Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money
06/03/2024 - 30/04/2024
1.    Thời gian triển khai:
06/3/2024 – 30/4/2024
2.    Phạm vi:
Toàn quốc.
3.    Đối tượng:
Khách hàng có tài khoản VNPT Money (tài khoản ví VNPT Pay định danh và liên kết ngân hàng hoặc có tài khoản Mobile Money định danh), đồng thời chưa từng thanh toán Điện hoặc Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 qua VNPT Money.
4.    Hình thức khuyến mại:
Trong thời gian triển khai chương trình, khách hàng sẽ được nhận một trong hai khuyến mại như sau:
- Khách hàng thanh toán Điện: sau khi thanh toán hoá đơn Điện với số tiền thực trả tối thiểu 300.000đ/giao dịch sẽ được hoàn 20.000đ vào tài khoản Ví VNPT Money/ Mobile Money.
- Khách hàng thanh toán Nước: sau khi thanh toán Nước với số tiền thực trả tối thiểu 100.000đ/giao dịch sẽ được hoàn 20.000đ vào tài khoản Ví VNPT Money/ Mobile Money.
(Các giao dịch thanh toán bằng nguồn tiền Ví VNPT Pay hoặc Tài khoản liên kết sẽ được hoàn tiền vào Ví VNPT Pay. Các giao dịch thanh toán bằng nguồn tiền Mobile Money sẽ được hoàn tiền vào Mobile Money).
(*) Số tiền thực trả: là số tiền Khách hàng thanh toán sau khi đã giảm trừ các ưu đãi khác nếu có.
(*) Không áp dụng cho giao dịch thanh toán bằng nguồn tiền thẻ ATM nội địa/ thẻ quốc tế/ thẻ visa
5. Điều khoản chung:
-    Mỗi khách hàng (01 số điện thoại và 01 CMND/ CCCD/Hộ chiếu) được nhận 01 lần ưu đãi/chương trình.
+    TH1: Nếu khách hàng đã từng thanh toán Điện và chưa từng thanh toán Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 thì khi Khách hàng thanh toán Nước (đáp ứng điều kiện chương trình) sẽ được nhận khuyến mại của chương trình và ngược lại.
+    TH2: Nếu khách hàng đã từng thanh toán Điện trong thời gian 01/6/2023 - 05/3/2024 , trong thời gian triển khai chương trình tiếp tục thanh toán Điện thì sẽ không được nhận khuyến mại của chương trình. Tương tự với dịch vụ Nước.
+    TH3: Nếu khách hàng chưa từng thanh toán cả Điện + Nước trong thời gian 01/6/2023 - 05/3/2024 trong thời gian triển khai chương trình Khách hàng thanh toán hoá đơn nào hợp lệ trước (Điện hoặc Nước) thì sẽ được nhận khuyến mại cho hoá đơn thanh toán lần đầu đó, đảm bảo mỗi khách hàng chỉ nhận 01 lần khuyến mại.
-    Trường hợp số lượng ưu đãi hết trước thời gian kết thúc chương trình, VNPT Money sẽ thông báo trên website https://vnptmoney.vn/web
-    Thời gian khách hàng nhận được ưu đãi: trong vòng 48h kể từ khi thanh toán thành công.
-    Các giao dịch đã được hưởng khuyến mại nếu khách hàng muốn hoàn/huỷ thì VNPT Money sẽ hoàn trả lại khách hàng phần giá trị sau khi đã trừ số tiền khuyến mại mà khách hàng được hưởng.
-    Các tài khoản tham gia chương trình phải là các tài khoản được đăng nhập bằng thiết bị di động cá nhân, không thông qua các công cụ giả lập khác.
-    VNPT Money có quyền bảo lưu việc trả thưởng để xem xét đối với các trường hợp được cho là có dấu hiệu gian lận hay lạm dụng.
-    Thời gian để tiếp nhận khiếu nại liên quan đến chương trình là trong vòng 02 ngày làm việc kể từ ngày kết thúc chương trình. Thời gian xử lý khiếu nại liên quan đến chương trình trong vòng 72h kể từ khi tiếp nhận khiếu nại. Sau thời gian này, VNPT Money không tiếp nhận các khiếu nại.
-    Trong các trường hợp khiếu nại, tranh chấp mọi quyết định thuộc về VNPT Money.
6. Tổng đài CSKH:
18001091 (nhánh 3)."""

prompt = template.format(title=title, link=link, content=content)
print(prompt)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
)
print(response.choices[0].message.content)

#########
# client = Client()
# output_dir = "output/response/"
# df = pd.read_csv("datasets/vnpt_money_data_1.0.csv")
# prompt = PredefinedPrompt()
# ANSWER_PROMPT = prompt.ANSWER_PROMPT
# CONDENSE_QUESTION_PROMPT = prompt.CONDENSE_QUESTION_PROMPT

# invalid_list = []
# for i in tqdm(range(len(df))):
#     try:
#         question, context = (
#             df.loc[i, "question"],
#             df.loc[i, "context"],
#         )
#         content = ANSWER_PROMPT.format(context=context, question=question)
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "user", "content": content}],
#         )
#         df.loc[i, "answer"] = response.choices[0].message.content.strip()
#     except Exception as e:
#         df.loc[i, "answer"] = ""
#         invalid_list.append(i)

# now = datetime.datetime.now()
# current_time_ft = now.strftime("%Y-%m-%d %H:%M")
# file_name = f"llm_{current_time_ft}.csv"
# output_path = f"{output_dir}gpt4_inference_{file_name}"
# df.to_csv(output_path, index=False)
# logger.info(f"Save llm'response in {output_path}")
