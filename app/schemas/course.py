"""Schémas Pydantic des cours et des séances."""

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.levels import Level


class CourseCreate(BaseModel):
    """Données reçues pour créer un cours ; les champs sont validés (longueurs, jour de 0 à 6, niveau)."""

    teacher_id: int
    title: str = Field(min_length=1, max_length=150)
    subject: str = Field(min_length=1, max_length=100)
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    zoom_link: str | None = Field(default=None, max_length=500)
    level: Level

    @model_validator(mode="after")
    def check_times(self):
        """Refuse un cours dont l'heure de fin n'est pas après l'heure de début (422)."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class CourseResponse(BaseModel):
    """Cours renvoyé par l'API."""

    id: int
    teacher_id: int
    title: str
    subject: str
    day_of_week: int
    start_time: time
    end_time: time
    zoom_link: str | None
    level: str

    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseModel):
    """Données reçues pour créer une séance : sa date et un lien Zoom facultatif."""

    date: datetime
    zoom_link: str | None = Field(default=None, max_length=500)


class SessionResponse(BaseModel):
    """Séance renvoyée par l'API."""

    id: int
    course_id: int
    date: datetime
    zoom_link: str | None

    model_config = ConfigDict(from_attributes=True)