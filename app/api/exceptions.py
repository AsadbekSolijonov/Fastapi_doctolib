from fastapi import HTTPException, status


class BaseAuthExpn(HTTPException):
    def __init__(self,
                 status_code: int = status.HTTP_401_UNAUTHORIZED,
                 detail: str = 'UnAuthorized',
                 headers: dict | None = None):
        self.status_code = status_code
        self.detail = detail
        update_headers = {"WWW-Authorization": 'Bearer'}
        if headers:
            headers.update(update_headers)
        super().__init__(status_code=self.status_code, detail=self.detail, headers=headers)


class InvalidToken(BaseAuthExpn):
    def __init__(self, detail: str = "Token expired old"):
        super().__init__(detail=detail)
