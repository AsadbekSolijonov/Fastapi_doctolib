from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select, Session

from app.api.security_utils.password import password_hash, verify_password, create_access_token, create_token_pair, \
    set_refresh_cookie, get_current_user, bearer_schema
from app.db.session import get_session
from app.models import User
from app.models.user import Role
from app.schema.auth import LoginIn
from app.schema.user import UserOut, UserCreate

auth_route = APIRouter()


@auth_route.post('/register', response_model=UserOut)
async def register(data: UserCreate, role: Role = Role.patient, session: Session = Depends(get_session)):
    db_data = User.model_validate(data)
    exists = session.exec(select(User).where(User.email == db_data.email)).first()

    if exists:
        raise HTTPException(status_code=400, detail=f"{db_data.email} email avval ham ro'yxatdan o'tgan")
    user = None

    if role == Role.patient:
        user = User(full_name=db_data.full_name,
                    email=db_data.email,
                    phone=db_data.phone,
                    role=role,
                    password=password_hash(db_data.password),
                    bio=db_data.bio)

    elif role == Role.doctor:
        user = User(full_name=db_data.full_name,
                    email=db_data.email,
                    phone=db_data.phone,
                    role=role,
                    password=password_hash(db_data.password),
                    bio=db_data.bio)
        # specialty_id muhim

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@auth_route.post('/login')
async def login(body: LoginIn, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Cridentials")

    access_token, refresh_token = create_token_pair({"sub": str(user.id)})

    # set cookie
    set_refresh_cookie(response, refresh_token)

    return access_token, refresh_token


@auth_route.post('/logout')
async def user_logout(request: Request,
                      response: Response,
                      user: Annotated[User, Depends(get_current_user)],
                      creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)]):
    pass
