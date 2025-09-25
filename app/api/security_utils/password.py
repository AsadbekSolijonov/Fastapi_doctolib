from datetime import datetime, timezone, timedelta
from typing import Optional, Type, Annotated

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.api.exceptions import NotAuthenticated, InvalidToken, TokenExpired, UserNotFound
from app.db.session import settings, get_session
from app.models import User

myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
bearer_scheme = HTTPBearer(auto_error=False)


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp_dt = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = {
        **data,
        "iat": int(now.timestamp()),  # issued-at (ixtiyoriy, tavsiya etiladi)
        "exp": int(exp_dt.timestamp()),  # MUHIM: int epoch seconds
        # "nbf": int(now.timestamp()),      # ixtiyoriy: not before (hozirgacha yaroqsiz)
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
        creds: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
        session: Annotated[Session, Depends(get_session)], ) -> Type[User]:
    # 1) Header tekshiruvi
    if not creds or creds.scheme.lower() != "bearer":
        raise NotAuthenticated()

    token = creds.credentials

    # 2) Tokenni dekodlash
    try:
        payload = jwt.decode(token, settings.SECRET_KEY.strip(), algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise InvalidToken()
        try:
            user_id = int(sub)  # agar sizda string/uuid bo'lsa, shu qatorni moslang
        except (TypeError, ValueError):
            raise InvalidToken()
    except ExpiredSignatureError:
        raise TokenExpired()
    except JWTError:
        raise InvalidToken()

    # 3) Foydalanuvchini DB’dan olish
    user = session.get(User, user_id)
    if not user:
        raise UserNotFound()

    return user
