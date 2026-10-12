from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CourseCreate(BaseModel):
    teacher_id: int
    title: str = Field(min_length=1, max_length=150)
    subject: str = Field(min_length=1, max_length=100)
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    zoom_link: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class CourseResponse(BaseModel):
    id: int
    teacher_id: int
    title: str
    subject: str
    day_of_week: int
    start_time: time
    end_time: time
    zoom_link: str | None

    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseModel):
    date: datetime
    zoom_link: str | None = Field(default=None, max_length=500)


class SessionResponse(BaseModel):
    id: int
    course_id: int
    date: datetime
    zoom_link: str | None

    model_config = ConfigDict(from_attributes=True)