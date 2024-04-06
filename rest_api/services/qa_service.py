from chatbot.chat import CustomerServiceChatbot
from rest_api.schemas.items import QueryItem

chatbot = CustomerServiceChatbot()


async def answer_question(query: QueryItem):
    """Answer the incoming question

    Args:
        query (QueryItem): incoming question

    Returns:
        Dict: the result of incoming question
    """
    # get chat history
    if isinstance(query, str):
        query = QueryItem(question=query)

    answer = chatbot.invoke(query=query)

    return answer
