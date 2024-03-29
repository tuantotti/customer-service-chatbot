from chatbot.chat import CustomerServiceChatbot
from utils.logger import Logger
from rest_api.services.qa_service import answer_question
from rest_api.schemas.items import QuestionItem

class TestQAService:
    def test_inference(self):
        logger = Logger.get_logger()
        question = "Có thể chuyển tiền từ Mobile Money của nhà mạng này sang nhà mạng khác cung cấp được không?"
        query = QuestionItem(question=question)
        response = answer_question(query=query)
        logger.info(response)