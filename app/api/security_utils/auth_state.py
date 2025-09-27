from typing import Annotated

from fastapi import Request, Depends, HTTPException, status

from app.api.security_utils.password import get_current_user
from app.models import User


async def auth_required(request: Request, user: Annotated[User, Depends(get_current_user)]):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='UnAuthorized')
    request.state.user = user
