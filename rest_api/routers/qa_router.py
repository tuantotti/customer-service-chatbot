from typing import AnyStr, Dict, List, Union

from fastapi import APIRouter

from rest_api.schemas.items import EmbeddingItem, QueryItem, QuestionItem
from rest_api.services.qa_service import (answer_question, embedd_service,
                                          generate)
from utils.logger import Logger

router = APIRouter(tags=["question_answering"])
logger = Logger.get_logger()


@router.post("/answer")
async def answer_question_router(question: QuestionItem) -> Dict:
    """API for answering incoming question

    Args:
        question (QuestionItem): incoming question

    Returns:
        Dict: the answer of incoming question
    """
    response = {}
    logger.info(question)
    try:
        answer = await answer_question(question=question)
        response["answer"] = answer
    except Exception as e:
        msg = f"Erorr {e}"
        response["message"] = msg

    return response


@router.post("/llm")
async def generate_content(question: QuestionItem) -> Dict:
    response = {}
    try:
        content = await generate(question)
        response["content"] = content
    except Exception as e:
        msg = f"Error {e}"
        response["message"] = msg

    return response


@router.post("/embedd")
async def embedd(text: EmbeddingItem) -> Dict:
    response = {}
    try:
        vectors = await embedd_service(text)
        response["vectors"] = vectors
    except Exception as e:
        msg = f"Error {e}"
        response["message"] = msg

    return response
