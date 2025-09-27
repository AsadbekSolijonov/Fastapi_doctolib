from fastapi import HTTPException, status


class BaseAuthExpn(HTTPException):
    def __init__(self,
                 status_code: int = status.HTTP_401_UNAUTHORIZED,
                 detail: str = 'UnAuthorized',
                 headers: dict | None = None):
        self.status_code = status_code
        self.detail = detail
        update_headers = {"WWW-Authenticated": 'Bearer'}
        if headers:
            headers.update(update_headers)
        super().__init__(status_code=self.status_code, detail=self.detail, headers=headers)


class ExpiredToken(BaseAuthExpn):
    def __init__(self, detail: str = "Token expired."):
        super().__init__(detail=detail)


class InvalidToken(BaseAuthExpn):
    def __init__(self, detail: str = "Invalid Token."):
        super().__init__(detail=detail)


class UserNotFound(BaseAuthExpn):
    def __init__(self, detail: str = "User not Found."):
        super().__init__(detail=detail)