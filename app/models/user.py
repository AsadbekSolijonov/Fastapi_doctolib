from datetime import datetime as ddt, timezone, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:  # circler import uchun
    from app.models.specialty import Specialty


class Role(str, Enum):
    patient = 'patient'
    doctor = 'doctor'
    admin = 'admin'


class User(SQLModel, table=True):
    __tablename__ = 'users'
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    password: str = Field(nullable=False)
    full_name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    role: Role = Field(nullable=False, default=Role.patient.value)
    bio: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    specialty_id: Optional[int] = Field(default=None, foreign_key='specialty.id')
    specialty: Optional["Specialty"] = Relationship(back_populates='users')
