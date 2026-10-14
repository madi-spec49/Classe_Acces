from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import require_role
from app.models import ParentStudent, User
from app.schemas.auth import UserRegister, UserResponse
from app.security import hash_password

router = APIRouter(prefix="/api/parents", tags=["parents"])


@router.post("", response_model=UserResponse)
def create_parent(
    payload: UserRegister,
    db: Session = Depends(get_db),
    staff: User = Depends(require_role("staff")),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    parent = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="parent",
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent


@router.post("/{parent_id}/students/{student_id}")
def link_parent_to_student(
    parent_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    staff: User = Depends(require_role("staff")),
):
    parent = db.get(User, parent_id)
    if parent is None or parent.role != "parent":
        raise HTTPException(status_code=404, detail="Parent not found")

    student = db.get(User, student_id)
    if student is None or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    link = db.get(ParentStudent, (parent_id, student_id))
    if link is None:
        db.add(ParentStudent(parent_id=parent_id, student_id=student_id))
        db.commit()

    return {"parent_id": parent_id, "student_id": student_id}