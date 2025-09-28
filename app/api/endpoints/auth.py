from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select, Session

from app.api.exceptions import InvalidToken, BlockedToken, UserNotFound
from app.api.security_utils.password import password_hash, verify_password, create_access_token, create_token_pair, \
    set_refresh_cookie, get_current_user, bearer_schema, decode_token, block_jti, \
    clear_refresh_cookie, is_jti_blocked, create_refresh_token, peek_jti_and_exp
from app.db.session import get_session, settings
from app.models import User
from app.models.user import Role
from app.schema.auth import LoginIn, Token
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

    payload = {"sub": str(user.id)}

    access_token, refresh_token = create_token_pair(data=payload)

    # set cookie
    set_refresh_cookie(response, refresh_token)

    return access_token


@auth_route.post('/logout')
async def user_logout(request: Request,
                      response: Response,
                      user: Annotated[User, Depends(get_current_user)],
                      # Logout qilish uchun login qilgan bo'lishi kerak.
                      creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)]):
    access_token = creds.credentials
    if creds and access_token and creds.scheme.lower() == 'bearer':
        p = decode_token(access_token, expected_type='access')
        block_jti(p.get('jti'), p.get('exp', 0))

    rt = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if rt:
        p = decode_token(rt, expected_type='refresh')
        block_jti(p.get('jti'), p.get('exp', 0))

    clear_refresh_cookie(response)
    return {"detail": "Logout Successfully!"}


@auth_route.post("/refresh")
async def refresh_access_token(request: Request, response: Response,
                               creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
                               session: Annotated[Session, Depends(get_session)]) -> Token:
    # 0) Access tokenni block qilamiz
    if creds and creds.credentials and creds.scheme.lower() == 'bearer':
        jti, exp_ts = peek_jti_and_exp(creds.credentials)
        if jti and exp_ts:
            block_jti(jti, exp_ts)

    rt = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    # 1) Refresh tokenni decode qilamiz
    payload = decode_token(rt, expected_type="refresh")

    # 2) Denylist tekshiruvi
    if is_jti_blocked(payload.get("jti")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    # 3) Userni olish
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad subject")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # 4) Accessni yangilash
    access = create_access_token({"sub": str(user.id)})

    # 5) Refresh rotatsiyasi:
    # eski refresh jti ni bloklab, yangisini berish (reuse aniqlash uchun ham foydali)
    block_jti(payload.get("jti"), int(payload.get("exp", 0)))
    new_refresh = create_refresh_token({"sub": str(user.id)})
    set_refresh_cookie(response, new_refresh)

    # 6) Yangi access tokenni qaytaramiz
    return access
