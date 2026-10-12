from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import require_role
from app.models import User
from app.schemas.auth import UserRegister, UserResponse
from app.security import hash_password

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.post("/teachers", response_model=UserResponse)
def create_teacher(
    data: UserRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    teacher = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role="teacher",
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
