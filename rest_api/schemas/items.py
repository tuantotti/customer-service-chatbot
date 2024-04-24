from enum import Enum
from typing import AnyStr, List, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    AI = "ai"


class ChatType(str, Enum):
    PRIVATE = "PRIVATE"


class QueryItem(BaseModel):
    question: AnyStr
    context: Optional[AnyStr] = Field(default="")


class QuestionItem(BaseModel):
    question: AnyStr


class AnswerItem(BaseModel):
    question: QuestionItem = Field(default=None)
    context: AnyStr = Field(default="")
    raw_context: List[Document]
    docs: List[Document]
    answer: AnyStr = Field(default=None)
    is_continue: bool = Field(default=False)


class MessageItem(BaseModel):
    role: Role
    score: Optional[int] = Field(default=-1)
    text: str


class CustomerChatItem(BaseModel):
    id: Optional[str] = Field(default=None)
    userId: Optional[str] = Field(default=None)
    messages: List[MessageItem]
    type: Optional[str] = Field(default=ChatType.PRIVATE)


class WebhookItem(BaseModel):
    webhook: str = Field(default=None)
