from pydantic import BaseModel, Field
from typing import List


class PollCreate(BaseModel):
    app_id: str
    entity_id: str
    question: str
    options: List[str] = Field(min_length=2)
    created_by: str


class Vote(BaseModel):
    user_id: str
    option_index: int = Field(ge=0)
