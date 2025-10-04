from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.branch import Branch
from app.schema.branch import BranchOut, BranchCreate, BranchUpdate
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=List[BranchOut])
def list_branches(db: Session = Depends(get_session),
                  limit: int = Query(100, ge=1, le=500),
                  offset: int = Query(0, ge=0)):
    q = select(Branch).offset(offset).limit(limit)
    return db.exec(q).all()


@router.get("/{branch_id}", response_model=BranchOut)
def get_branch(branch_id: int, db: Session = Depends(get_session)):
    obj = db.get(Branch, branch_id)
    if not obj:
        raise HTTPException(404, "Branch not found")
    return obj


@router.post("", response_model=BranchOut, status_code=201)
def create_branch(payload: BranchCreate, db: Session = Depends(get_session)):
    try:
        payload = Branch.model_validate(payload)
        db.add(payload)
        db.commit()
        db.refresh(payload)
        return payload
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"{e.orig}")


@router.patch("/{branch_id}", response_model=BranchOut)
def update_branch(branch_id: int, payload: BranchUpdate, db: Session = Depends(get_session)):
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
