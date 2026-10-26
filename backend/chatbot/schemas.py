"""Data shapes: the model's structured reply and the API's request bodies."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class BotAnswer(BaseModel):
    """The structured reply the model must return."""

    answer: str = Field(description="The reply to show the user, in the language of their latest message.")
    sources: list[str] = Field(default_factory=list, description="Source URLs from search results that support the answer.")
    answered: bool = Field(description="False when the search results did not contain the answer.")
    medical_topic: bool = Field(description="True if the answer discusses treatments, conditions or outcomes.")
    wants_quote: bool = Field(description="True if the user asks about booking, quotes, contact, or a price not listed.")


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=12)

    @field_validator("messages")
    @classmethod
    def ends_with_user(cls, messages: list[Message]) -> list[Message]:
        if messages[-1].role != "user":
            raise ValueError("last message must be from the user")
        return messages


class LeadRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=EMAIL_PATTERN, max_length=200)
    question: str = Field(default="", max_length=1000)
