from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgressCreate(BaseModel):
    student_id: int
    course_id: int
    level: str = Field(min_length=1, max_length=50)
    note: Optional[str] = None


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    teacher_id: int
    level: str
    note: Optional[str] = None
    date: datetime