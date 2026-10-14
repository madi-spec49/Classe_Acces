from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user, require_role
from app.models import AttendanceRecord, Course, CourseSession, EnrollmentRequest, User
from app.schemas.attendance import AttendanceCreate, AttendanceResponse

router = APIRouter(prefix="/api/sessions", tags=["attendance"])


def get_session_and_course(session_id: int, db: Session):
    course_session = db.get(CourseSession, session_id)
    if course_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    course = db.get(Course, course_session.course_id)
    return course_session, course


@router.post("/{session_id}/attendance", response_model=AttendanceResponse)
def record_attendance(
    session_id: int,
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_role("teacher")),
):
    course_session, course = get_session_and_course(session_id, db)

    if course.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Not your course")

    enrollment = (
        db.query(EnrollmentRequest)
        .filter(
            EnrollmentRequest.student_id == payload.student_id,
            EnrollmentRequest.course_id == course.id,
            EnrollmentRequest.status == "approved",
        )
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this course")

    record = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == payload.student_id,
        )
        .first()
    )
    if record is None:
        record = AttendanceRecord(session_id=session_id, student_id=payload.student_id)
        db.add(record)

    record.status = payload.status
    record.note = payload.note
    db.commit()
    db.refresh(record)
    return record


@router.get("/{session_id}/attendance", response_model=list[AttendanceResponse])
def list_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course_session, course = get_session_and_course(session_id, db)
    if user.role != "staff" and course.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()