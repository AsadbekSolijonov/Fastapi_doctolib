from fastapi import HTTPException, status


class BaseHTTPExceptoin(HTTPException):
    def __int__(self, status_code: int = status.HTTP_401_UNAUTHORIZED, detail: str = "Unauthorized",
                headers: dict | None = None) -> None:
        base_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            base_headers.update(headers)
        super().__init__(status_code=status_code, detail=detail, headers=base_headers)


class NotAuthenticated(BaseHTTPExceptoin):
    def __init__(self, detail="Not authenticated") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidToken(BaseHTTPExceptoin):
    def __init__(self, detail="Invalid Token") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class TokenExpired(BaseHTTPExceptoin):
    def __init__(self, detail="Token expired") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserNotFound(BaseHTTPExceptoin):
    def __init__(self, detail="Invalid token (user not found)") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
