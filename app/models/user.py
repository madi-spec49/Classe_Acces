from sqlalchemy import CheckConstraint, Column, Integer, String, Boolean, DateTime, func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'parent', 'teacher', 'staff')", name="ck_users_role"),
        CheckConstraint("level IN ('debutant', 'intermediaire', 'avance')", name="ck_users_level"),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")
    level = Column(String(20), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
