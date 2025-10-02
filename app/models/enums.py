from enum import Enum


class Role(str, Enum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"


class AppointmentStatus(str, Enum):
    pending = "pending"
    active = "active"
    finished = "finished"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"


class Weekday(str, Enum):
    mon = "Mon"
    tue = "Tue"
    wed = "Wed"
    thu = "Thu"
    fri = "Fri"
    sat = "Sat"
    sun = "Sun"
