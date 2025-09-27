from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select, Session

from app.api.security_utils.password import password_hash, verify_password, create_token_pair, \
    set_refresh_cookie, clear_refresh_cookie, get_current_user, bearer_schema, decode_token, block_jti
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
    paylod = {"sub": str(user.id)}
    access_token, refresh_token = create_token_pair(data=paylod)
    # Refresh tokenni HttpOnly cookie'da beramiz (JS ko'rmaydi)
    set_refresh_cookie(response, refresh_token)

    return access_token


@auth_route.post('/logout')
async def logout(request: Request,
                 response: Response,
                 current_user: Annotated[User, Depends(get_current_user)],
                 creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)]):
    # 1) Access header bo'lsa — revoke
    if creds and (creds.scheme or "").lower() == "bearer" and creds.credentials:
        try:
            p = decode_token(creds.credentials, expected_type="access")
            block_jti(p.get("jti"), int(p.get("exp", 0)))
        except Exception:
            # access noto'g'ri bo'lsa ham davom etamiz
            pass

    # 2) Refresh cookie bo'lsa — revoke
    rt = request.cookies.get("refresh_token")
    if rt:
        try:
            p = decode_token(rt, expected_type="refresh")
            block_jti(p.get("jti"), int(p.get("exp", 0)))
        except Exception:
            pass
    clear_refresh_cookie(response)
    return {"detail": "Logout successfully!"}
