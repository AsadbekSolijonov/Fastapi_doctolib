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

myctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_schema = HTTPBearer(auto_error=False)

_BLOCKED_JTIS: dict[str, int] = {}  # jti -> exp_ts


def _now_utc():
    return datetime.now(timezone.utc)


def _now_ts() -> int:
    return int(_now_utc().timestamp())


def block_jti(jti: str, exp_ts: int) -> None:
    if jti and exp_ts:
        _BLOCKED_JTIS[jti] = exp_ts


def _gc_blocked() -> None:
    now = _now_ts()
    for jti, exp in list(_BLOCKED_JTIS.items()):
        print(f"exp: {exp}, now: {now}", end=">>>")
        if exp <= now:
            print(f" done")
            _BLOCKED_JTIS.pop(jti, None)
        else:
            print(f" not done")


def is_jti_blocked(jti: str) -> bool:
    if not jti:
        return False
    _gc_blocked()
    return jti in _BLOCKED_JTIS


def peek_jti_and_exp(token: str) -> tuple[str | None, int]:
    try:
        claims = jwt.get_unverified_claims(token)
        return claims.get('jti'), int(claims.get('exp', 0))
    except JWTError:
        return None, 0


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)


def create_access_token(data: dict, expire_minutes: int | None = None) -> str:
    now = _now_utc()
    exp_dt = now + timedelta(minutes=expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        **data,
        'type': 'access',
        'jti': str(uuid4()),
        'iat': int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }
    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


def create_refresh_token(data: dict, expire_days: int | None = None) -> str:
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


def create_token_pair(data: dict) -> tuple[str, str]:
    return create_access_token(data), create_refresh_token(data)


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()

    token_type = payload.get('type')

    if token_type != expected_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'Decode Token expected ‘{expected_type}‘, but got ‘{token_type}‘.')
    return payload


def get_current_user(
        creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
        session: Annotated[Session, Depends(get_session)]) -> Type[User]:
    if not creds or creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Cridentials were not provided!")

    token = creds.credentials
    payload = decode_token(token, expected_type='access')
    sub = payload.get('sub')

    jti = payload.get('jti')
    if is_jti_blocked(jti):
        print(f"119: {_BLOCKED_JTIS}")
        raise InvalidToken('Token blocked.')
    print(f"124: {_BLOCKED_JTIS}")
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidToken('Bad subject')

    user = session.get(User, user_id)
    if not user:
        raise UserNotFound()
    return user


def set_refresh_cookie(response: Response, refresh_token, max_ages: int | None = None) -> None:
    if max_ages is None:
        max_ages = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=max_ages,
        httponly=True,
        # prod: secure=True
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(settings.REFRESH_COOKIE_NAME)
