from fastapi import APIRouter

user_route = APIRouter()


@user_route.get('/')
async def user():
    return {"msg": "User"}
