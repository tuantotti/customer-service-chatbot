from typing import AnyStr, Dict, Union

from fastapi import APIRouter

from rest_api.schemas.items import QueryItem
from rest_api.services.qa_service import answer_question

router = APIRouter(tags=["question_answering"])


@router.post("/answer")
async def answer_question_router(question: Union[QueryItem]) -> Dict:
    """API for answering incoming question

    Args:
        question (Union[QueryItem]): incoming question

    Returns:
        Dict: the answer of incoming question
    """
    response = {}
    try:
        answer = await answer_question(query=question)
        response["answer"] = answer
    except Exception as e:
        msg = f"Erorr {e}"
        response["message"] = msg

    return response
