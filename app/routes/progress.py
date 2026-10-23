from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user, require_role
from app.models import Course, ParentStudent, ProgressRecord, User
from app.schemas.progress import ProgressCreate, ProgressResponse

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.post("", response_model=ProgressResponse)
def record_progress(
    payload: ProgressCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_role("teacher")),
):
    course = db.get(Course, payload.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Not your course")

    student = db.get(User, payload.student_id)
    if student is None or student.role != "student" or student.level != course.level:
        raise HTTPException(status_code=400, detail="Student is not in this course level")

    record = ProgressRecord(
        student_id=payload.student_id,
        course_id=course.id,
        teacher_id=teacher.id,
        level=payload.level,
        note=payload.note,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/students/{student_id}", response_model=list[ProgressResponse])
def list_student_progress(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "staff" or user.id == student_id:
        allowed = True
    elif user.role == "parent":
        link = db.get(ParentStudent, (user.id, student_id))
        allowed = link is not None
    elif user.role == "teacher":
        student = db.get(User, student_id)
        allowed = (
            student is not None
            and student.level is not None
            and db.query(Course)
            .filter(Course.teacher_id == user.id, Course.level == student.level)
            .first() is not None
        )
    else:
        allowed = False

    if not allowed:
        raise HTTPException(status_code=403, detail="Access denied")

    return (
        db.query(ProgressRecord)
        .filter(ProgressRecord.student_id == student_id)
        .order_by(ProgressRecord.date)
        .all()
    )