from typing import List, Annotated

import status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.security_utils.password import password_hash, verify_password, create_access_token, get_current_user
from app.db.session import get_session
from app.models import User
from app.models.user import Role
from pydantic import EmailStr

from app.schema.auth import LoginIn, Token
from app.schema.user import UserOut, UserCreate, UserBase

user_route = APIRouter()


@user_route.get('/', response_model=List[UserOut])
async def list_users(*, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail='Users not found.')
    return users


@user_route.post('/register', response_model=UserOut)
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


@user_route.post('/login')
async def login(body: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Cridentials")

    user_token = create_access_token({"sub": str(user.id)}, expire_minutes=1)
    return user_token


@user_route.get('/me', response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
