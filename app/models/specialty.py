from typing import TYPE_CHECKING, Optional, List
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:  # circle import uchun
    from app.models.user import User


class Specialty(SQLModel, table=True):
    __tablename__ = 'specialty'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    descripition: Optional[str] = Field(default=None)

    users: List["User"] = Relationship(back_populates="specialty")
