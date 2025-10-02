from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import AppointmentStatus

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.branch import Room
    from app.models.user import User
    from app.models.payment import Payment


class Appointment(SQLModel, table=True):  # Uchrashuv vaqti
    __tablename__ = "appointment"
    id: Optional[int] = Field(default=None, primary_key=True)

    doctor_id: Optional[int] = Field(foreign_key="users.id", ondelete='SET NULL', nullable=True)
    patient_id: int = Field(foreign_key='users.id', ondelete='CASCADE', nullable=False)
    room_id: int = Field(foreign_key="room.id", ondelete='SET NULL', nullable=True)

    start_at: datetime = Field(nullable=False)
    end_at: datetime = Field(nullable=False)
    status: "AppointmentStatus" = Field(default=AppointmentStatus.pending, nullable=False)
    note: Optional[str] = Field(default=None)

    # patient: "User" = Relationship(back_populates="patient_appointments",
    #                                sa_relationship_kwargs={"foreign_keys": ["Appointment.patient_id"]})
    # doctor: Optional["User"] = Relationship(back_populates="doctor_appointments",
    #                                         sa_relationship_kwargs={"foreign_keys": ["Appointment.doctor_id"]})
    room: Optional["Room"] = Relationship(back_populates="appointments")

    payments: List["Payment"] = Relationship(back_populates="appointment")
    status_history: List['AppointmentStatusHistory'] = Relationship(back_populates="appointment")


class AppointmentStatusHistory(SQLModel, table=True):
    __tablename__ = "appointment_status_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="appointment.id", nullable=False)
    old_status: AppointmentStatus = Field(nullable=False)
    new_status: AppointmentStatus = Field(nullable=False)
    changed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    changed_by: Optional[int] = Field(foreign_key="users.id", default=None)

    appointment: "Appointment" = Relationship(back_populates="status_history")
    changed_by_user: Optional["User"] = Relationship(back_populates="status_changes")
