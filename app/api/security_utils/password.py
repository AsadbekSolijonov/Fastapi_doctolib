from typing import Annotated, Type

from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from sqlmodel import Session

from app.api.exceptions import ExpiredToken, InvalidToken, UserNotFound
from app.db.session import settings, get_session
from app.models import User
from app.schema.auth import Token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
bearer_schema = HTTPBearer(auto_error=False)


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expire_minutes: int | None = None):
    now = datetime.now(timezone.utc)
    exp_dt = now + timedelta(minutes=expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        **data,
        'iat': int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }
    jwt_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return Token(access_token=jwt_token)


def get_current_user(
        creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
        session: Annotated[Session, Depends(get_session)]) -> Type[User]:
    if not creds or creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Cridentials were not provided!")

    token = creds.credentials

    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()
    sub = data.get('sub')
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidToken('Bad subject')

    user = session.get(User, user_id)
    if not user:
        raise UserNotFound()
    return user
