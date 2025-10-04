from fastapi import APIRouter

from app.api.endpoints import (auth_route, user_route, specialties_router,
                               schedules_router, appointments_router,
                               branches_router, sections_router, rooms_router,
                               payments_router)

api_router = APIRouter()
api_router.include_router(auth_route, prefix='/auth', tags=['Auth'])
api_router.include_router(user_route, prefix='/users', tags=['User'])
api_router.include_router(specialties_router)
api_router.include_router(schedules_router)
api_router.include_router(appointments_router)
api_router.include_router(branches_router)
api_router.include_router(sections_router)
api_router.include_router(rooms_router)
api_router.include_router(payments_router)
