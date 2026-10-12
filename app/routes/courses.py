from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user, require_role
from app.models import Course, User
from app.schemas.course import CourseCreate, CourseResponse

router = APIRouter(prefix="/api/courses", tags=["courses"])


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