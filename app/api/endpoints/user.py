from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.security_utils.password import password_hash, verify_password
from app.db.session import get_session
from app.models import User
from app.models.user import Role
from pydantic import EmailStr
from app.schema.user import UserOut, UserCreate, UserBase

user_route = APIRouter()


@user_route.get('/', response_model=List[UserOut])
async def list_users(*, session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail='Users not found.')
    return users


@user_route.post('/', response_model=UserOut)
async def create_user(data: UserCreate, role: Role = Role.patient, session: Session = Depends(get_session)):
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
async def create_user(login: EmailStr, password: str, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == login)).first()

    if not exists:
        raise HTTPException(status_code=400, detail=f"Bunday foydalanuvchi topilmadi.")

    if verify_password(password, exists.password):
        return {"login": "Successfully"}
    else:
        return {"err": "Login yoki parol xato."}

# UPDATE | DELETE
