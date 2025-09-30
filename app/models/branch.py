from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class Brach(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    address: str = Field(nullable=False)

    sections: list['Section'] = Relationship(back_populates='branch')


class Section(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)

    branch_id = Field(foreign_key='branch.id', unique=True)
    branch = Relationship(back_populates='sections')

    rooms = Relationship(back_populates='section')


class Room(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    floor: int = Field(nullable=False)
    door_number: int = Field(nullable=False)

    doctor_id: User | None = Field(default=None, foreign_key='users.id')
    doctors: list['User'] = Relationship(back_populates='room')

    section_id: Section = Field(nullable=False, foreign_key='section.id')
    section = Relationship(back_populates='rooms')
