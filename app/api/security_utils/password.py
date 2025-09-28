from typing import Annotated, Type
from uuid import uuid4

from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, ExpiredSignatureError, JWTError
from sqlmodel import Session

from app.api.exceptions import ExpiredToken, InvalidToken, UserNotFound
from app.db.session import settings, get_session
from app.models import User
from app.schema.auth import Token
from fastapi import Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
bearer_schema = HTTPBearer(auto_error=False)

_BLOCKED_JTIS: dict = {}


def _now_utc():
    return datetime.now(timezone.utc)


def blocked_jti(jti, exp_dt):
    if jti and exp_dt:
        _BLOCKED_JTIS[jti] = exp_dt


def _gc_blocked():
    now = _now_utc().timestamp()
    for jti, exp in _BLOCKED_JTIS.items():
        if exp > now:
            _BLOCKED_JTIS.pop(jti)


def is_jti_blocked(jti: str):
    if not jti:
        return False
    _gc_blocked()
    return jti in _BLOCKED_JTIS


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expire_minutes: int | None = None):
    now = _now_utc()
    exp_dt = now + timedelta(minutes=expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        **data,
        'type': 'access',
        'jti': str(uuid4()),
        'iat': int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }
    jwt_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return Token(access_token=jwt_token)


def create_refresh_token(data: dict, expire_days: int | None = None):
    now = datetime.now(timezone.utc)
    exp_dt = now + timedelta(days=expire_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        **data,
        'type': 'refresh',
        'jti': str(uuid4()),
        "iat": int(now.timestamp()),
        'exp': int(exp_dt.timestamp()),
    }
    ref_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return ref_token


def create_token_pair(data: dict):
    return create_access_token(data), create_refresh_token(data)


def decode_token(token: str, excepted_type: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()

    token_type = payload.get('type')

    if token_type != excepted_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Decode Token expected ‘{excepted_type}‘, but got ‘{token_type}‘.')
    return payload


def get_current_user(
        creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
        session: Annotated[Session, Depends(get_session)]) -> Type[User]:
    if not creds or creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Cridentials were not provided!")

    token = creds.credentials
    payload = decode_token(token, excepted_type='access')
    jti = payload.get('jti')

    if is_jti_blocked(jti):
        raise InvalidToken('Token blocked.')

    sub = payload.get('sub')
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidToken('Bad subject')

    user = session.get(User, user_id)
    if not user:
        raise UserNotFound()
    return user


def set_refresh_cookie(response: Response, refresh_token, max_ages: int | None = None):
    if max_ages is None:
        max_ages = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_ages,
        httponly=True
    )


