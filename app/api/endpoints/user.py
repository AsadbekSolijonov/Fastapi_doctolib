from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlmodel import Session, select

from app.api.security_utils.auth_state import auth_required
from app.api.security_utils.password import get_current_user
from app.db.session import get_session
from app.models import User, Role

from app.schema.user import UserOut, UserUpdate

# user_route = APIRouter(dependencies=[Depends(auth_required)])
user_route = APIRouter()


@user_route.get('/', response_model=List[UserOut])
async def list_users(role: Optional[Role] = Query(None),
                     search_full_name: Optional[str] = Query(None),
                     limit: int = Query(50, ge=1, le=200),
                     offset: int = Query(0, ge=0),
                     db: Session = Depends(get_session)):
    q = select(User)
    if role:
        q = q.where(User.role == role)

    if search_full_name:
        q = q.where(User.full_name.like(f"{search_full_name}%"))
    return db.exec(q.offset(offset).limit(limit)).all()


@user_route.get('/me', response_model=UserOut)
async def get_me(request: Request):
    return request.state.user


@user_route.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_session)):
    obj = db.get(User, user_id)
    if not obj:
        raise HTTPException(404, "User not found")
    return obj


@user_route.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_session)):
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
