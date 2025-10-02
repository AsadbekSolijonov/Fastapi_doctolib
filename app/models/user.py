from datetime import datetime as ddt, timezone, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import Role

if TYPE_CHECKING:  # circler import uchun
    from app.models import Specialty, Appointment, AppointmentStatusHistory


class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    role: Role = Field(nullable=False, default=Role.patient)
    bio: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    # ONE-TO-MANY SPECIALTY varianti:
    specialty_id: Optional[int] = Field(default=None, foreign_key='specialty.id')
    specialty: Optional["Specialty"] = Relationship(back_populates='users')

    # Appointments (ikki tomonga ajratilgan)
    # doctor_appointments: list["Appointment"] = Relationship(
    #     back_populates="doctor",
    #     sa_relationship_kwargs={"foreign_keys": ["Appointment.doctor_id"]}
    # )
    # patient_appointments: list["Appointment"] = Relationship(
    #     back_populates="patient",
    #     sa_relationship_kwargs={"foreign_keys": ["Appointment.patient_id"]}
    # )

    # Status history author relationship (agar kerak bo‘lsa)
    status_changes: list["AppointmentStatusHistory"] = Relationship(back_populates="changed_by_user")
