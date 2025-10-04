from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.branch import Section
from app.schema.branch import SectionOut, SectionCreate, SectionUpdate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/sections", tags=["sections"])


@router.get("", response_model=List[SectionOut])
def list_sections(db: Session = Depends(get_session),
                  branch_id: int | None = None,
                  limit: int = Query(100, ge=1, le=500),
                  offset: int = Query(0, ge=0)):
    q = select(Section)
    if branch_id is not None:
        q = q.where(Section.branch_id == branch_id)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{section_id}", response_model=SectionOut)
def get_section(section_id: int, db: Session = Depends(get_session)):
    obj = db.get(Section, section_id)
    if not obj:
        raise HTTPException(404, "Section not found")
    return obj


@router.post("", response_model=SectionOut, status_code=201)
def create_section(payload: SectionCreate, db: Session = Depends(get_session)):
    try:
        payload = Section.model_validate(payload)
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"{e.orig}")


@router.patch("/{section_id}", response_model=SectionOut)
def update_section(section_id: int, payload: SectionUpdate, db: Session = Depends(get_session)):
    obj = db.get(Section, section_id)
    if not obj:
        raise HTTPException(404, "Section not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{section_id}", status_code=204)
def delete_section(section_id: int, db: Session = Depends(get_session)):
    obj = db.get(Section, section_id)
    if not obj:
        raise HTTPException(404, "Section not found")
    db.delete(obj)
    db.commit()
