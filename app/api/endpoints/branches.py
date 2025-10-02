from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.branch import Branch

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=List[Branch])
def list_branches(db: Session = Depends(get_session),
                  limit: int = Query(100, ge=1, le=500),
                  offset: int = Query(0, ge=0)):
    q = select(Branch).offset(offset).limit(limit)
    return db.exec(q).all()


@router.get("/{branch_id}", response_model=Branch)
def get_branch(branch_id: int, db: Session = Depends(get_session)):
    obj = db.get(Branch, branch_id)
    if not obj:
        raise HTTPException(404, "Branch not found")
    return obj


@router.post("", response_model=Branch, status_code=201)
def create_branch(payload: Branch, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@router.patch("/{branch_id}", response_model=Branch)
def update_branch(branch_id: int, payload: Branch, db: Session = Depends(get_session)):
    obj = db.get(Branch, branch_id)
    if not obj:
        raise HTTPException(404, "Branch not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{branch_id}", status_code=204)
def delete_branch(branch_id: int, db: Session = Depends(get_session)):
    obj = db.get(Branch, branch_id)
    if not obj:
        raise HTTPException(404, "Branch not found")
    db.delete(obj)
    db.commit()
