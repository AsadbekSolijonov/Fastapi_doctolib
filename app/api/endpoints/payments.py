from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.payment import Payment
from app.models.enums import PaymentStatus, PaymentMethod

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=List[Payment])
def list_payments(
        db: Session = Depends(get_session),
        appointment_id: int | None = None,
        status: PaymentStatus | None = None,
        method: PaymentMethod | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
):
    q = select(Payment)
    if appointment_id is not None:
        q = q.where(Payment.appointment_id == appointment_id)
    if status is not None:
        q = q.where(Payment.status == status)
    if method is not None:
        q = q.where(Payment.method == method)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, db: Session = Depends(get_session)):
    obj = db.get(Payment, payment_id)
    if not obj:
        raise HTTPException(404, "Payment not found")
    return obj


@router.post("", response_model=Payment, status_code=201)
def create_payment(payload: Payment, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{payment_id}", response_model=Payment)
def update_payment(payment_id: int, payload: Payment, db: Session = Depends(get_session)):
    obj = db.get(Payment, payment_id)
    if not obj:
        raise HTTPException(404, "Payment not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{payment_id}", status_code=204)
def delete_payment(payment_id: int, db: Session = Depends(get_session)):
    obj = db.get(Payment, payment_id)
    if not obj:
        raise HTTPException(404, "Payment not found")
    db.delete(obj)
    db.commit()
