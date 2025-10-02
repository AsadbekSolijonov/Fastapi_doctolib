from fastapi import APIRouter
from app.api.endpoints.user import user_route
from app.api.endpoints.branches import router as branches_router
from app.api.endpoints.sections import router as sections_router
from app.api.endpoints.rooms import router as rooms_router
from app.api.endpoints.appointments import router as appointments_router
from app.api.endpoints.payments import router as payments_router
from app.api.endpoints.specialties import router as specialties_router
from app.api.endpoints.schedules import router as schedules_router
from app.api.endpoints.auth import auth_route
from app.api.endpoints.user import user_route

api_router = APIRouter()
api_router.include_router(auth_route, prefix='/auth', tags=['Auth'])
api_router.include_router(user_route, prefix='/users', tags=['User'])
api_router.include_router(branches_router)
api_router.include_router(sections_router)
api_router.include_router(rooms_router)
api_router.include_router(appointments_router)
api_router.include_router(payments_router)
api_router.include_router(specialties_router)
api_router.include_router(schedules_router)
