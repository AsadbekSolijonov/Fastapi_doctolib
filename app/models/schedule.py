from typing import Optional
from datetime import time
from sqlmodel import SQLModel, Field, Relationship, CheckConstraint, UniqueConstraint

from .enums import Weekday
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class DoctorSchedule(SQLModel, table=True):
    __tablename__ = "doctor_schedule"
    __table_args__ = (
        UniqueConstraint("doctor_id", "weekday", "start_time", "end_time", name="uq_doctor_slot"),
        CheckConstraint("start_time < end_time", name="ck_schedule_time"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="users.id", nullable=False)
    weekday: Weekday = Field(nullable=False)
    start_time: time = Field(nullable=False)
    end_time: time = Field(nullable=False)

    doctor: "User" = Relationship()
