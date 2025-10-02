from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.branch import Section

router = APIRouter(prefix="/sections", tags=["sections"])


@router.get("", response_model=List[Section])
def list_sections(db: Session = Depends(get_session),
                  branch_id: int | None = None,
                  limit: int = Query(100, ge=1, le=500),
                  offset: int = Query(0, ge=0)):
    q = select(Section)
    if branch_id is not None:
        q = q.where(Section.branch_id == branch_id)
    return db.exec(q.offset(offset).limit(limit)).all()


@router.get("/{section_id}", response_model=Section)
def get_section(section_id: int, db: Session = Depends(get_session)):
    obj = db.get(Section, section_id)
    if not obj:
        raise HTTPException(404, "Section not found")
    return obj


@router.post("", response_model=Section, status_code=201)
def create_section(payload: Section, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{section_id}", response_model=Section)
def update_section(section_id: int, payload: Section, db: Session = Depends(get_session)):
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
