from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class AttendanceCreate(BaseModel):
    student_id: int
    status: Literal["present", "absent", "late"]
    note: Optional[str] = None


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    student_id: int
    status: str
    note: Optional[str] = None
    created_at: datetime