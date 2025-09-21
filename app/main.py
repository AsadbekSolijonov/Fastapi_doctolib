from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title='Fast API doctolib', version='1.0.0', lifespan=lifespan)

app.include_router(api_router, prefix='/api/v1')
