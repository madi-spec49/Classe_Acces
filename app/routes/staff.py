from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_db
from app.dependencies import require_role
from app.models import User
from app.schemas.auth import PasswordReset, StudentCreate, UserRegister, UserResponse
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



@router.post("/students", response_model=UserResponse)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    student = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role="student",
        level=data.level,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.get("/teachers")
def list_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    teachers = (
        db.query(User)
        .filter(User.role == "teacher")
        .order_by(User.last_name, User.first_name)
        .all()
    )
    return [
        {"id": t.id, "first_name": t.first_name, "last_name": t.last_name}
        for t in teachers
    ]


@router.get("/students")
def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    students = (
        db.query(User)
        .filter(User.role == "student")
        .order_by(User.last_name, User.first_name)
        .all()
    )
    return [
        {"id": s.id, "first_name": s.first_name, "last_name": s.last_name}
        for s in students
    ]


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    users = (
        db.query(User)
        .filter(User.role != "staff")
        .order_by(User.last_name, User.first_name)
        .all()
    )
    return [
        {"id": u.id, "first_name": u.first_name, "last_name": u.last_name, "role": u.role}
        for u in users
    ]


@router.post("/users/{user_id}/password")
def reset_password(
    user_id: int,
    data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("staff")),
):
    user = db.get(User, user_id)
    if user is None or user.role == "staff":
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.password)
    db.commit()
    return {"id": user.id}
