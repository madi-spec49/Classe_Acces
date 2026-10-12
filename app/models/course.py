from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, SmallInteger, String, Time

from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_courses_day"),
        CheckConstraint("end_time > start_time", name="ck_courses_times"),
    )

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    day_of_week = Column(SmallInteger, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    zoom_link = Column(String(500))


class CourseSession(Base):
    __tablename__ = "course_sessions"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    zoom_link = Column(String(500))