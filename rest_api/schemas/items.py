from enum import Enum
from typing import AnyStr, Optional

from pydantic import BaseModel


class QueryItem(BaseModel):
    question: AnyStr
    context: Optional[AnyStr] = None


class QuestionItem(BaseModel):
    question: AnyStr
