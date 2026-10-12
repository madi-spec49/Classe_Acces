from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentDecision(BaseModel):
    status: Literal["approved", "rejected"]


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    requested_by_id: int
    status: str
    handled_by_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)