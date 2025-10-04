from sqlmodel import SQLModel


# ==================================
# Branch
# ==================================

class BranchCreate(SQLModel):
    name: str
    address: str


class BranchOut(SQLModel):
    id: int
    name: str
    address: str


class BranchUpdate(SQLModel):
    name: str | None = None
    address: str | None = None


# ==================================
# Saction
# ==================================

class SectionCreate(SQLModel):
    name: str
    branch_id: int


class SectionOut(SQLModel):
    id: int
    name: str
    branch_id: int


class SectionUpdate(SQLModel):
    name: str | None = None
    branch_id: int | None = None


# ==================================
# Room
# ==================================

class RoomCreate(SQLModel):
    floor: int
    door_number: int
    section_id: int


class RoomOut(SQLModel):
    id: int
    floor: int
    door_number: int
    section_id: int


class RoomUpdate(SQLModel):
    floor: int | None = None
    door_number: int | None = None
    section_id: int | None = None
