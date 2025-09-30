from datetime import datetime

from sqlmodel import SQLModel
from pydantic import EmailStr


class UserBase(SQLModel):
    full_name: str
    email: EmailStr
    phone: str
    bio: str | None = None


class UserOut(UserBase):  # ReadOnly
    id: int
    role: str
    created_at: datetime


class UserCreate(UserBase):  # Write Only (PUT/CREATE)
    password: str
    specialty_id: int | None = None


class UserUpdate(UserBase):  # PATCH Partial
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    bio: str | None = None
