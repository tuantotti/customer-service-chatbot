from enum import Enum
from typing import AnyStr, List, Optional, Union

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    AI = "ai"


class ChatType(str, Enum):
    PRIVATE = "PRIVATE"


class QueryItem(BaseModel):
    question: AnyStr
    context: Optional[AnyStr] = Field(default="")


class EmbeddingItem(BaseModel):
    text: Union[AnyStr, List]


class QuestionItem(BaseModel):
    question: AnyStr


class AnswerItem(BaseModel):
    question: AnyStr = Field(default="")
    context: List = Field(default="")
    raw_context: List = Field(default=[])
    docs: List = Field(default=[])
    answer: AnyStr = Field(default="")
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
