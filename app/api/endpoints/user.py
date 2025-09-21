from fastapi import APIRouter

user_route = APIRouter(prefix='/users', tags=['User CRUD'])


@user_route.get('/')
async def user():
    return {"msg": "User"}
