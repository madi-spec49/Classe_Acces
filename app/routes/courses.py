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
    if current_user.role == "student":
        return (
            db.query(Course)
            .filter(Course.level == current_user.level)
            .order_by(Course.id)
            .all()
        )
    return db.query(Course).order_by(Course.id).all()


@router.post("/{course_id}/sessions", response_model=SessionResponse)
def create_session(
    course_id: int,
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = get_course_or_404(course_id, db)
    if current_user.role != "staff" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

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



@router.get("/{course_id}/students")
def list_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = get_course_or_404(course_id, db)
    if current_user.role != "staff" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    students = (
        db.query(User)
        .filter(User.role == "student", User.level == course.level)
        .order_by(User.last_name, User.first_name)
        .all()
    )
    return [
        {"id": s.id, "first_name": s.first_name, "last_name": s.last_name}
        for s in students
    ]

@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Le staff peut supprimer n'importe quel cours, le professeur seulement les siens.
    course = get_course_or_404(course_id, db)
    if current_user.role != "staff" and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Les séances, présences et progressions liées sont supprimées en cascade.
    db.delete(course)
    db.commit()
    return {"deleted": course_id}
