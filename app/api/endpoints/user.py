from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlmodel import Session, select

from app.api.security_utils.auth_state import auth_required
from app.api.security_utils.password import get_current_user
from app.db.session import get_session
from app.models import User

from app.schema.user import UserOut

user_route = APIRouter(dependencies=[Depends(auth_required)])


@user_route.get('/', response_model=List[UserOut])
async def list_users(*, session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@user_route.get('/me', response_model=UserOut)
async def get_me(request: Request):
    return request.state.user


@user_route.get("", response_model=List[User])
def list_users(
        db: Session = Depends(get_session),
        role: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
):
    q = select(User)
    if role:
        q = q.where(User.role == role)
    return db.exec(q.offset(offset).limit(limit)).all()


@user_route.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_session)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    return obj


@user_route.post("", response_model=User, status_code=201)
def create_user(payload: User, db: Session = Depends(get_session)):
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


@user_route.patch("/{user_id}", response_model=User)
def update_user(user_id: int, payload: User, db: Session = Depends(get_session)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@user_route.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    db.delete(obj)
    db.commit()
