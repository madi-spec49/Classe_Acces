"""Schémas Pydantic de la progression des élèves."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgressCreate(BaseModel):
    """Données reçues pour saisir une progression : élève, cours, niveau atteint et note facultative."""

    student_id: int
    course_id: int
    level: str = Field(min_length=1, max_length=50)
    note: Optional[str] = None


class ProgressResponse(BaseModel):
    """Progression renvoyée par l'API, avec la matière et le titre du cours."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    teacher_id: int
    level: str
    note: Optional[str] = None
    date: datetime
    course_subject: Optional[str] = None
    course_title: Optional[str] = None