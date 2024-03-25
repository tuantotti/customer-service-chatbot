from typing import AnyStr, Union

from chatbot.chat import CustomerServiceChatbot
from rest_api.schemas.items import QueryItem

chatbot = CustomerServiceChatbot()


async def answer_question(query: Union[QueryItem, AnyStr]):
    # get chat history
    if isinstance(query, str):
        query = QueryItem(question=query)

    answer = chatbot.invoke(query=query)

    return answer
