from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
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
