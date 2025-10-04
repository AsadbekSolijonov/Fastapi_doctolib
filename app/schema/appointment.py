from datetime import datetime

from sqlmodel import SQLModel


class AppointmentOut(SQLModel):
    id: int
    doctor_id: int
    patient_id: int
    room_id: int
    start_at: datetime
    end_at: datetime
    note: str


class AppointmentCreate(SQLModel):
    doctor_id: int
    patient_id: int
    room_id: int
    start_at: datetime
    end_at: datetime
    note: str | None = None


class AppointmentUpdate(SQLModel):  # partial
    doctor_id: int | None = None
    patient_id: int | None = None
    room_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    note: str | None = None
