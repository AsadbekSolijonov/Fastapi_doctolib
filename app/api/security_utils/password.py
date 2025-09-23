from passlib.context import CryptContext

myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])


def password_hash(password: str):
    return myctx.hash(password)


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return myctx.verify(plain_pwd, hashed_pwd)
