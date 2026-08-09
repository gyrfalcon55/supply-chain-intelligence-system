from pydantic import BaseModel
from typing import Any

class ChatResponse(BaseModel):
    answer: str

class TableResponse(BaseModel):
    table: list[dict[str, Any]]
    