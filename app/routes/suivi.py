from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user
from app.models import AttendanceRecord, Course, CourseSession, ParentStudent, User

router = APIRouter(prefix="/api/students", tags=["suivi"])


def can_view_student(user: User, student_id: int, db: Session) -> bool:
    if user.role == "staff" or user.id == student_id:
        return True
    if user.role == "parent":
        return db.get(ParentStudent, (user.id, student_id)) is not None
    return False


@router.get("/{student_id}/attendance")
def list_student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not can_view_student(user, student_id, db):
        raise HTTPException(status_code=403, detail="Access denied")

    rows = (
        db.query(AttendanceRecord, CourseSession, Course)
        .join(CourseSession, AttendanceRecord.session_id == CourseSession.id)
        .join(Course, CourseSession.course_id == Course.id)
        .filter(AttendanceRecord.student_id == student_id)
        .order_by(CourseSession.date)
        .all()
    )
    return [
        {
            "session_id": session.id,
            "date": session.date,
            "subject": course.subject,
            "title": course.title,
            "status": record.status,
            "note": record.note,
        }
        for record, session, course in rows
    ]
