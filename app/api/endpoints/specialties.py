from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.specialty import Specialty

router = APIRouter(prefix="/specialties", tags=["specialties"])


@router.get("", response_model=List[Specialty])
def list_specialties(db: Session = Depends(get_session),
                     limit: int = Query(100, ge=1, le=500),
                     offset: int = Query(0, ge=0)):
    q = select(Specialty).offset(offset).limit(limit)
    return db.exec(q).all()


@router.get("/{specialty_id}", response_model=Specialty)
def get_specialty(specialty_id: int, db: Session = Depends(get_session)):
    obj = db.get(Specialty, specialty_id)
    if not obj:
        raise HTTPException(404, "Specialty not found")
    return obj


@router.post("", response_model=Specialty, status_code=201)
def create_specialty(payload: Specialty, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{specialty_id}", response_model=Specialty)
def update_specialty(specialty_id: int, payload: Specialty, db: Session = Depends(get_session)):
    obj = db.get(Specialty, specialty_id)
    if not obj:
        raise HTTPException(404, "Specialty not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{specialty_id}", status_code=204)
def delete_specialty(specialty_id: int, db: Session = Depends(get_session)):
    obj = db.get(Specialty, specialty_id)
    if not obj:
        raise HTTPException(404, "Specialty not found")
    db.delete(obj)
    db.commit()
