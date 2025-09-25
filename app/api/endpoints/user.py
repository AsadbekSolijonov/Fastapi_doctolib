from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.api.security_utils.password import (
    password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.db.session import get_session
from app.models import User
from app.models.user import Role
from app.schema.auth import LoginIn, Token
from app.schema.user import UserOut, UserCreate

user_route = APIRouter()


@user_route.get("/", response_model=List[UserOut], summary="List users")
async def list_users(
        session: Annotated[Session, Depends(get_session)],
):
    users = session.exec(select(User)).all()
    # Odatda bo'sh ro'yxat 200 OK bilan []
    return users


@user_route.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register",
)
async def register(
        data: UserCreate,
        # Agar roldni query orqali berishni xohlasangiz (aks holda UserCreate ichiga qo'shib yuboring)
        role: Annotated[Role, Query(description="User role")] = Role.patient,
        session: Annotated[Session, Depends(get_session)] = None,
):
    # Email unikalmi?
    exists = session.exec(select(User).where(User.email == data.email)).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{data.email} email avval ham ro'yxatdan o'tgan",
        )

    # Parolni xeshlaymiz va foydalanuvchini yaratamiz
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        role=role,
        password=password_hash(data.password),
        bio=data.bio,
    )
    # TODO: agar role == doctor bo'lsa, specialty_id talab qilinadi

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@user_route.post(
    "/auth/login",
    response_model=Token,
    summary="Login and get access token (Bearer)",
)
async def login(
        body: LoginIn,
        session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password):
        # 401 va Bearer headeri — OAuth2 kliеntlar uchun to‘g‘ri semantika
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer")


@user_route.get("/me", response_model=UserOut, summary="Get current user")
async def me(
        current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
