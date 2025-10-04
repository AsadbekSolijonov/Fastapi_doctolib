from typing import Optional

from sqlmodel import SQLModel


class SpecialtyCreate(SQLModel):
    name: str
    description: Optional[str] | None = None


class SpecialtyOut(SQLModel):
    id: int
    name: str
    description: Optional[str]


class SpecialtyUpdate(SQLModel):
    name: str | None = None
    description: Optional[str] = None
