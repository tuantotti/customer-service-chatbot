# Scrapy settings for crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from datetime import datetime

import dotenv

dotenv.load_dotenv()

BOT_NAME = "crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "crawler (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "crawler.middlewares.CrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "crawler.middlewares.CrawlerDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "crawler.pipelines.CleanDocumentPipeline": 299,
    "crawler.pipelines.MongoPipeline": 300,
    "crawler.pipelines.SyntheticDataPipeline": 301,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

file_name = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
FEEDS = {f"output/{file_name}.json": {"format": "json", "encoding": "utf-8"}}

# Database settings
MONGO_URI = os.environ["MONGO_URI"]
MONGO_DATABASE = os.environ["MONGO_DATABASE"]
MILVUS_URI = os.environ["MILVUS_URI"]
MILVUS_COLLECTION = os.environ["MILVUS_COLLECTION"]
MILVUS_USER = os.environ["MILVUS_USER"]
MILVUS_PASSWORD = os.environ["MILVUS_PASSWORD"]
LLM_API = os.environ["LLM_API"]
EMBEDDING_API = os.environ["EMBEDDING_API"]
GEMINI_API = os.environ["GEMINI_API"]

directory = "logs/crawler/promotion_crawler/"
if not os.path.exists(directory):
    os.makedirs(directory)
LOG_FILE = f"{directory}/{file_name}.log"


CHUNKING_PROMPT = """
Công việc của bạn là tách đoạn văn thành các phần ngắn hơn nhưng vẫn phải đảm bảo ngữ nghĩa trong một phần. Nếu bạn không chia được thành đừng phần hãy trả về đoạn văn ban đầu.
Các phần cần ngăn cách nhau bởi chuỗi "*********"
Để tôi cho bạn xem một ví dụ:
Đoạn văn:
Hoàn 20% nộp phí chung cư qua VNPT Money
24/04/2024 - 31/07/2024
1.    Thời gian triển khai:
24/4/2024 – 31/7/2024
2.    Phạm vi:
Toàn quốc.
3.    Đối tượng:
Khách hàng có tài khoản VNPT Money (có tài khoản Ví VNPT Pay định danh, liên kết ngân hàng hoặc có tài khoản Mobile Money định danh theo quy định).

Các đoạn được tách:
*********
Hoàn 20% nộp phí chung cư qua VNPT Money 24/04/2024 - 31/07/2024
*********
1.    Thời gian triển khai: 24/4/2024 – 31/7/2024
*********
2.    Phạm vi: Toàn quốc.
*********
3.    Đối tượng: Khách hàng có tài khoản VNPT Money (có tài khoản Ví VNPT Pay định danh, liên kết ngân hàng hoặc có tài khoản Mobile Money định danh theo quy định)
*********

Hãy chia đoạn văn dưới đây thành các phần. Lưu ý không thêm bất kỳ ký tự nào khi bạn chia thành các phần:
Đoạn văn:
{text}
Các đoạn được tách:
"""

SYNTHETIC_PROMPT = """Bạn là chuyên gia về chăm sóc khác hàng. Công việc của bạn là tạo ra dữ liệu câu hỏi thực tế của khách hàng bằng tiếng Việt về chương trình khuyến mãi sản phẩm. Giọng điệu trong câu trả lời của nhân viên chăm sóc khác hàng phải trang trọng, ấm áp và lịch sự. Mỗi cặp câu hỏi, câu trả lời phải ngăn cách nhau bởi chuỗi "************"; giữa câu hỏi và câu trả lời ngăn cách bởi chuỗi "******".20 câu hỏi được tạo ra phải chứa tên chương trình khuyến mãi, không sử dụng tên thay thế nào khác. Các câu trả lời được tạo ra cần chèn LINK KHUYẾN MÃI nếu bạn thấy hợp lý.
Dưới đây là một ví dụ về 4 câu hỏi dựa trên chương trình khuyến mãi:
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money
LINK KHUYẾN MÃI: https://vnptpay.vn/web/khuyenmai/diennuoc0324
THÔNG TIN KHUYẾN MÃI: 
1. Thời gian triển khai:
06/3/2024 – 30/4/2024
2. Phạm vi:
Toàn quốc.
3. Đối tượng: Khách hàng có tài khoản VNPT Money (tài khoản ví VNPT Pay định danh và liên kết ngân hàng hoặc có tài khoản Mobile Money định danh), đồng thời chưa từng thanh toán Điện hoặc Nước trong khoảng thời gian 01/6/2023 - 05/3/2024 qua VNPT Money.

4 câu hỏi:
************
Khách hàng: Tôi muốn tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money. Xin cho tôi biết thời gian triển khai là khi nào?
******
Khách hàng: Chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money áp dụng ở phạm vi nào?
******
Khách hàng: Đối tượng nào được tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money?
******
Khách hàng: Cần có điều kiện gì để tham gia chương trình khuyến mãi Tiết kiệm 20.000đ thanh toán Điện, Nước qua VNPT Money?
************

Dựa vào ví dụ mà tôi đã cung cấp, hãy tạo ra 20 câu hỏi với cấu trúc giống với ví dụ dựa trên thông tin CHƯƠNG TRÌNH KHUYẾN MÃI dưới đây: 
CHƯƠNG TRÌNH KHUYẾN MÃI
TÊN CHƯƠNG TRÌNH KHUYẾN MÃI: {title}
LINK KHUYẾN MÃI: {link} 
THÔNG TIN KHUYẾN MÃI: "{content}" 

20 câu hỏi:
"""
