from chatbot.chat import CustomerServiceChatbot
from rest_api.schemas.items import QuestionItem

chatbot = CustomerServiceChatbot()


async def answer_question(query: QuestionItem):
    """Answer the incoming question

    Args:
        query (QuestionItem): incoming question

    Returns:
        Dict: the result of incoming question
    """
    # get chat history
    if isinstance(query, str):
        query = QuestionItem(question=query)

    answer = chatbot.invoke(query=query)

    return answer
