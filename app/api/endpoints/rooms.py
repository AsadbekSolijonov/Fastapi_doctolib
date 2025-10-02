from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.branch import Room

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=List[Room])
def list_rooms(db: Session = Depends(get_session),
               section_id: int | None = None,
               limit: int = Query(100, ge=1, le=500),
               offset: int = Query(0, ge=0)):
    q = select(Room)
    if section_id is not None:
        q = q.where(Room.section_id == section_id)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: int, db: Session = Depends(get_session)):
    obj = db.get(Room, room_id)
    if not obj:
        raise HTTPException(404, "Room not found")
    return obj


@router.post("", response_model=Room, status_code=201)
def create_room(payload: Room, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{room_id}", response_model=Room)
def update_room(room_id: int, payload: Room, db: Session = Depends(get_session)):
    obj = db.get(Room, room_id)
    if not obj:
        raise HTTPException(404, "Room not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{room_id}", status_code=204)
def delete_room(room_id: int, db: Session = Depends(get_session)):
    obj = db.get(Room, room_id)
    if not obj:
        raise HTTPException(404, "Room not found")
    db.delete(obj)
    db.commit()
