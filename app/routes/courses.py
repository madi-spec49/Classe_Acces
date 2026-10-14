from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user, require_role
from app.models import Course, CourseSession, User
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    SessionCreate,
    SessionResponse,
)

router = APIRouter(prefix="/api/courses", tags=["courses"])


def get_course_or_404(course_id: int, db: Session) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("", response_model=CourseResponse)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    teacher = db.query(User).filter(User.id == data.teacher_id).first()
    if teacher is None or teacher.role != "teacher":
        raise HTTPException(status_code=400, detail="teacher_id must be a teacher account")

    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Course).order_by(Course.id).all()


@router.post("/{course_id}/sessions", response_model=SessionResponse)
def create_session(
    course_id: int,
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    get_course_or_404(course_id, db)

    course_session = CourseSession(course_id=course_id, **data.model_dump())
    db.add(course_session)
    db.commit()
    db.refresh(course_session)
    return course_session


@router.get("/{course_id}/sessions", response_model=list[SessionResponse])
def list_sessions(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_course_or_404(course_id, db)

    return (
        db.query(CourseSession)
        .filter(CourseSession.course_id == course_id)
        .order_by(CourseSession.date)
        .all()
    )
