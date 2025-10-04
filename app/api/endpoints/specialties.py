from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session
from app.models import User
from app.models.specialty import Specialty
from app.schema.specialty import SpecialtyOut, SpecialtyCreate, SpecialtyUpdate

router = APIRouter(prefix="/specialties", tags=["specialties"])


@router.get("", response_model=List[SpecialtyOut])
def list_specialties(sp: Optional[str] = Query(None),
                     db: Session = Depends(get_session),
                     limit: int = Query(100, ge=1, le=500),
                     offset: int = Query(0, ge=0)):
    q = select(Specialty)
    if sp:
        q = q.where(Specialty.name.like(f"{sp}%"))
    q = q.offset(offset).limit(limit)
    return db.exec(q).all()


@router.get("/{specialty_id}", response_model=SpecialtyOut)
def get_specialty(specialty_id: int, db: Session = Depends(get_session)):
    obj = db.get(Specialty, specialty_id)
    if not obj:
        raise HTTPException(404, "Specialty not found")
    return obj


@router.post("", response_model=SpecialtyOut, status_code=201)
def create_specialty(payload: SpecialtyCreate, db: Session = Depends(get_session)):
    try:
        paylod = Specialty.model_validate(payload)
        db.add(paylod)
        db.commit()
        db.refresh(paylod)
        return paylod
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="UNIQUE constraint failed: specialty.name")


@router.patch("/{specialty_id}", response_model=SpecialtyOut)
def update_specialty(specialty_id: int, payload: SpecialtyUpdate, db: Session = Depends(get_session)):
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
