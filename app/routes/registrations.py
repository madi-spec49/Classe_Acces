from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import get_current_user, require_role
from app.models import Course, EnrollmentRequest, User
from app.schemas.registration import (
    EnrollmentCreate,
    EnrollmentDecision,
    EnrollmentResponse,
)

router = APIRouter(prefix="/api/registrations", tags=["registrations"])


@router.post("", response_model=EnrollmentResponse)
def request_enrollment(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    course = db.query(Course).filter(Course.id == data.course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(EnrollmentRequest)
        .filter(
            EnrollmentRequest.student_id == current_user.id,
            EnrollmentRequest.course_id == data.course_id,
            EnrollmentRequest.status.in_(["pending", "approved"]),
        )
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="Enrollment already requested")

    enrollment = EnrollmentRequest(
        student_id=current_user.id,
        course_id=data.course_id,
        requested_by_id=current_user.id,
        status="pending",
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("", response_model=list[EnrollmentResponse])
def list_enrollments(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    query = db.query(EnrollmentRequest)
    if status is not None:
        query = query.filter(EnrollmentRequest.status == status)
    return query.order_by(EnrollmentRequest.id).all()


@router.patch("/{enrollment_id}", response_model=EnrollmentResponse)
def decide_enrollment(
    enrollment_id: int,
    data: EnrollmentDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    enrollment = (
        db.query(EnrollmentRequest)
        .filter(EnrollmentRequest.id == enrollment_id)
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment request not found")
    if enrollment.status != "pending":
        raise HTTPException(status_code=400, detail="Request already handled")

    enrollment.status = data.status
    enrollment.handled_by_id = current_user.id
    db.commit()
    db.refresh(enrollment)
    return enrollment
