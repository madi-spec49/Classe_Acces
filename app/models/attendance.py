from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func

from app.models.base import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        CheckConstraint("status IN ('present', 'absent', 'late')", name="ck_attendance_status"),
        UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"),
    )

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("course_sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())