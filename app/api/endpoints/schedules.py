from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.schedule import DoctorSchedule
from app.models.enums import Weekday

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=List[DoctorSchedule])
def list_schedules(db: Session = Depends(get_session),
                   doctor_id: int | None = None,
                   weekday: Weekday | None = None,
                   limit: int = Query(100, ge=1, le=500),
                   offset: int = Query(0, ge=0)):
    q = select(DoctorSchedule)
    if doctor_id is not None:
        q = q.where(DoctorSchedule.doctor_id == doctor_id)
    if weekday is not None:
        q = q.where(DoctorSchedule.weekday == weekday)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{schedule_id}", response_model=DoctorSchedule)
def get_schedule(schedule_id: int, db: Session = Depends(get_session)):
    obj = db.get(DoctorSchedule, schedule_id)
    if not obj:
        raise HTTPException(404, "Schedule not found")
    return obj


@router.post("", response_model=DoctorSchedule, status_code=201)
def create_schedule(payload: DoctorSchedule, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{schedule_id}", response_model=DoctorSchedule)
def update_schedule(schedule_id: int, payload: DoctorSchedule, db: Session = Depends(get_session)):
    obj = db.get(DoctorSchedule, schedule_id)
    if not obj:
        raise HTTPException(404, "Schedule not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: int, db: Session = Depends(get_session)):
    obj = db.get(DoctorSchedule, schedule_id)
    if not obj:
        raise HTTPException(404, "Schedule not found")
    db.delete(obj)
    db.commit()
