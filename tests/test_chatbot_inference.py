from chatbot.chat import CustomerServiceChatbot
from utils.logger import Logger

class TestChatbot:
    def test_inference(self):
        logger = Logger.get_logger()
        question = "Có thể chuyển tiền từ Mobile Money của nhà mạng này sang nhà mạng khác cung cấp được không?"
        chatbot = CustomerServiceChatbot(use_retriever=True)
        response = chatbot.chain.invoke({"question": question})
        logger.info(response)
        