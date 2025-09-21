from typing import Generator

from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=True,
    connect_args={"check_same_thread": False} if settings.database_url.startswith('sqlite') else {}
)


def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.execute(text("PRAGMA foreign_keys=ON"))


def get_session() -> Generator:
    with Session(engine) as session:
        yield session
