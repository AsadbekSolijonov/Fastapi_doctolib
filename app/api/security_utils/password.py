from typing import Annotated, Type, Optional
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


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(data: dict, expire_minutes: int | None = None):
    now = _now_utc()
    exp_dt = now + timedelta(minutes=expire_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        **data,
        "type": 'access',
        "jti": str(uuid4()),
        'iat': int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }
    jwt_access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return Token(access_token=jwt_access_token)


def create_refresh_token(data: dict, expire_days: int | None = None):
    now = datetime.now(timezone.utc)
    exp_dt = now + timedelta(days=expire_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        **data,
        'type': 'refresh',
        'jti': str(uuid4()),  # rotation/reuse detection uchun
        "iat": int(now.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }
    jwt_refresh_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return jwt_refresh_token


def create_token_pair(data: dict) -> tuple[Token, str]:
    return create_access_token(data), create_refresh_token(data)


# ---- Token tekshirish ----
def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise ExpiredToken()
    except JWTError:
        raise InvalidToken()

    t = payload.get('type')
    if t != expected_type:
        # noto'g'ri turdagi token bilan kirishga urinish
        raise InvalidToken(f"Wrong token type: expected: ‘{expected_type}‘, got ‘{t}‘")
    return payload


# ---- Current user (faqat ACCESS token) ----
def get_current_user(creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
                     session: Annotated[Session, Depends(get_session)]) -> Type[User]:
    if not creds or creds.scheme.lower() != 'bearer':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Cridentials were not provided!")

    token = creds.credentials
    payload = decode_token(token, expected_type="access")
    sub = payload.get('sub')

    if is_jti_blocked(payload.get("jti")):
        raise InvalidToken("Token revoked")

    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise InvalidToken('Bad subject')

    user = session.get(User, user_id)

    if not user:
        raise UserNotFound()

    return user


# ---- (Ixtiyoriy) Refresh cookie utili ----
def set_refresh_cookie(response: Response, refresh_token: str, max_age_seconds: int | None = None):
    if max_age_seconds is None:
        max_age_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    # Prod: Secure=True va HTTPS ishlating
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        max_age=max_age_seconds,
        samesite="lax",
        path='/'
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path='/')


# === Denylist (demo: xotirada). Prod: Redis/DB tavsiya ===
_BLOCKED_JTIS: dict[str, int] = {}  # jti -> exp_ts


def _now_ts() -> int:
    return int(_now_utc().timestamp())


def _gc_blocked():
    now = _now_ts()
    for k, v in list(_BLOCKED_JTIS.items()):
        if v <= now:
            _BLOCKED_JTIS.pop(k, None)


def block_jti(jti: str, exp_ts: int) -> None:
    if jti and exp_ts:
        _BLOCKED_JTIS[jti] = int(exp_ts)


def is_jti_blocked(jti: Optional[str]) -> bool:
    if not jti:
        return False
    _gc_blocked()
    return jti in _BLOCKED_JTIS
