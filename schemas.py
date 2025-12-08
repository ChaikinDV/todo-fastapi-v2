from pydantic import BaseModel, ConfigDict
from typing import Optional


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

    model_config = ConfigDict(from_attributes=True)