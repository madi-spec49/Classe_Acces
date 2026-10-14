from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer

from app.models.base import Base


class ParentStudent(Base):
    __tablename__ = "parent_student"
    __table_args__ = (
        CheckConstraint("parent_id <> student_id", name="ck_parent_not_student"),
    )

    parent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)