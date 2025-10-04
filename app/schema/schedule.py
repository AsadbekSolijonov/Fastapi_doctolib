from datetime import time

from sqlmodel import SQLModel

from app.models import Weekday


class DoctorScheduleCreate(SQLModel):
    doctor_id: int
    weekday: Weekday
    start_time: time
    end_time: time


class DoctorScheduleOut(SQLModel):
    id: int
    doctor_id: int
    weekday: Weekday
    start_time: time
    end_time: time


class DoctorScheduleUpdate(SQLModel):
    doctor_id: int | None = None
    weekday: Weekday | None = None
    start_time: time | None = None
    end_time: time | None = None

