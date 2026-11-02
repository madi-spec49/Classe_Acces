"""Schémas Pydantic de l'assiduité : données reçues et données renvoyées."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class AttendanceCreate(BaseModel):
    """Données reçues pour saisir une présence ; le statut est limité à trois valeurs."""

    student_id: int
    status: Literal["present", "absent", "late"]
    note: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Présence renvoyée par l'API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    student_id: int
    status: str
    note: Optional[str] = None
    created_at: datetime