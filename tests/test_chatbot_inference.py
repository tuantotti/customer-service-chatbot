from chatbot.chat import CustomerServiceChatbot
from utils.logger import Logger

class TestChatbot:
    def test_inference(self):
        logger = Logger.get_logger()
        question = "Bạn là ai, bạn tên là gì, do công ty nào tạo ra hoặc phát triển?"
        chatbot = CustomerServiceChatbot(use_retriever=True)
        response = chatbot.invoke({"question": question})
        logger.info(response)
        