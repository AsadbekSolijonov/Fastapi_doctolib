from fastapi import APIRouter

from app.api.endpoints.user import user_route

api_router = APIRouter()
api_router.include_router(user_route, prefix='/users', tags=['User CRUD'])
