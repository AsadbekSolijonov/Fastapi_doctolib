from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Appointment, AppointmentStatusHistory
from app.models.enums import AppointmentStatus
from app.schema.appointment import AppointmentOut, AppointmentCreate, AppointmentUpdate

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=List[AppointmentOut])
def list_appointments(
        db: Session = Depends(get_session),
        doctor_id: int | None = None,
        patient_id: int | None = None,
        status: Optional[AppointmentStatus] = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
):
    q = select(Appointment)
    if doctor_id is not None:
        q = q.where(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        q = q.where(Appointment.patient_id == patient_id)
    if status is not None:
        q = q.where(Appointment.status == status)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_session)):
    obj = db.get(Appointment, appointment_id)
    if not obj:
        raise HTTPException(404, "Appointment not found")
    return obj


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_session)):
    obj = db.get(Appointment, appointment_id)
    if not obj:
        raise HTTPException(404, "Appointment not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(appointment_id: int, db: Session = Depends(get_session)):
    obj = db.get(Appointment, appointment_id)
    if not obj:
        raise HTTPException(404, "Appointment not found")
    db.delete(obj)
    db.commit()


# --- Status history ---

@router.get("/{appointment_id}/history", response_model=List[AppointmentStatusHistory])
def get_history(appointment_id: int, db: Session = Depends(get_session)):
    q = select(AppointmentStatusHistory).where(AppointmentStatusHistory.appointment_id == appointment_id)
    return db.exec(q.order_by(AppointmentStatusHistory.changed_at)).all()


@router.post("/{appointment_id}/status", response_model=Appointment)
def change_status(appointment_id: int, new_status: AppointmentStatus, note: str | None = None,
                  db: Session = Depends(get_session)):
    obj = db.get(Appointment, appointment_id)
    if not obj:
        raise HTTPException(404, "Appointment not found")

    old = obj.status
    if old == new_status:
        return obj

    obj.status = new_status
    if note:
        obj.note = (obj.note + "\n" if obj.note else "") + f"[status] {note}"

    db.add(obj)
    db.commit()
    db.refresh(obj)
    # Agar DB trigger ulangan bo‘lsa, history row avtomatik tushadi.
    # Trigger bo'lmasa, shu yerda qo‘shing:
    # db.add(AppointmentStatusHistory(appointment_id=appointment_id, old_status=old, new_status=new_status))
    # db.commit()
    return obj
