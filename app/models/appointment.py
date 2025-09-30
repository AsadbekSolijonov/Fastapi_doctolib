from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class Status(str, Enum):
    pending = "peding"
    cancelled = "cancelled"
    finished = "finished"
    active = "active"


class Appointment(SQLModel, table=True):  # Uchrashuv vaqti
    id: int | None = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="users.id", ondelete='CASCADE')
    patient_id: int = Field(foreign_key='users.id', ondelete='CASCADE')
    started_at: datetime = Field(nullable=False)
    fineshed_at: datetime = Field(nullable=False)
    status: Status = Field(nullable=False, default=Status.pending.value())



