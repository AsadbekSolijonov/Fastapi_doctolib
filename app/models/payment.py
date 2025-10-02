from typing import Optional
from datetime import datetime
from decimal import Decimal
from .enums import PaymentStatus, PaymentMethod
from sqlmodel import SQLModel, Field, Relationship, Column, Numeric, String, CheckConstraint

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Payment(SQLModel, table=True):
    __tablename__ = "payment"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_amount_positive"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # FK-ni ondelete bilan ishonchli berish uchun sa_column ishlatamiz
    appointment_id: int = Field(foreign_key="appointment.id", ondelete="CASCADE", nullable=False, index=True)

    # Moliyaviy qiymatlar: Decimal (Python) + Numeric(18,2) (DB)
    amount: Decimal = Field(sa_column=Column(Numeric(18, 2), nullable=False))

    # ISO valyuta kodi (masalan, "UZS", "USD")
    currency: str = Field(sa_column=Column(String(3), nullable=False, default="UZS"))

    method: PaymentMethod = Field(nullable=False)
    status: PaymentStatus = Field(default=PaymentStatus.pending, nullable=False)
    paid_at: Optional[datetime] = Field(default=None)

    # Kvitan­siya / tranzaksiya raqami (ixtiyoriy, lekin ko‘pincha noyob bo‘ladi)
    reference: Optional[str] = Field(sa_column=Column(String(64), unique=True, nullable=True))

    appointment: "Appointment" = Relationship(back_populates="payments")
