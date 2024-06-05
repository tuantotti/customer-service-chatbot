from typing import AnyStr, List, Union

from chatbot.chat import CustomerServiceChatbot
from rest_api.schemas.items import AnswerItem, QueryItem, QuestionItem, EmbeddingItem

chatbot = CustomerServiceChatbot()


async def answer_question(question: QuestionItem) -> AnswerItem:
    """Answer the incoming question

    Args:
        question (QuestionItem): incoming question

    Returns:
        Dict: the result of incoming question
    """

    answer = chatbot.invoke(query=question)

    return answer


async def generate(question: QuestionItem):
    """Answer the incoming question

    Args:
        question (AnyStr): incoming question

    Returns:
        Dict: the result of incoming question
    """
    answer = chatbot.llm.invoke(question.question)

    return answer


async def embedd_service(embedding_item: EmbeddingItem) -> List:
    """Embedd the incoming texts

    Args:
        embedding_item (EmbeddingItem): the incoming texts

    Returns:
        List: the vector representation of incoming texts
    """
    vectors = []
    text = embedding_item.text
    if isinstance(text, str):
        vectors = [chatbot.embedding_model.embed_query(text)]

    if isinstance(text, list):
        vectors = chatbot.embedding_model.embed_documents(text)

    return vectors
