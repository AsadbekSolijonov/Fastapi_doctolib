from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint, CheckConstraint
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from app.models.appointment import Appointment


class Branch(SQLModel, table=True):
    __tablename__ = 'branch'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    address: str = Field(nullable=False)

    sections: list['Section'] = Relationship(back_populates='branch')


class Section(SQLModel, table=True):
    __tablename__ = 'section'
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)

    branch_id: int = Field(foreign_key='branch.id', nullable=False)
    branch: "Branch" = Relationship(back_populates='sections')

    rooms: list["Room"] = Relationship(back_populates='section')


class Room(SQLModel, table=True):
    __tablename__ = 'room'
    __table_args__ = (
        UniqueConstraint('section_id', 'door_number', name='uq_section_door'),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    floor: int = Field(nullable=False)
    door_number: int = Field(nullable=False)

    appointments: List["Appointment"] = Relationship(back_populates='room')

    section_id: int = Field(foreign_key='section.id', nullable=False)
    section: "Section" = Relationship(back_populates='rooms')


class RoomClosure(SQLModel, table=True):
    __tablename__ = "room_closure"
    __table_args__ = (
        CheckConstraint("closed_from < closed_to", name="ck_closure_time"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.id", nullable=False)
    closed_from: datetime = Field(nullable=False)
    closed_to: datetime = Field(nullable=False)
    reason: Optional[str] = Field(default=None)

    room: "Room" = Relationship()
