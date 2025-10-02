from sqlmodel import SQLModel, Field
from app.models.enums import AppointmentStatus


class AppointmentStatusTransition(SQLModel, table=True):
    __tablename__ = "appointment_status_transition"

    # Kompozit PK: (from_status, to_status)
    from_status: AppointmentStatus = Field(primary_key=True, nullable=False)
    to_status: AppointmentStatus = Field(primary_key=True, nullable=False)


# Faqat ma’lumot uchun
ALLOWED_TRANSITIONS = [
    ("pending", "active"),
    ("pending", "cancelled"),
    ("active", "finished"),
    ("active", "cancelled"),
]
