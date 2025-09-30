from logging.config import fileConfig
import os
import pkgutil
import importlib

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# 1) App config (.env) dan URL olish
from app.core.config import get_settings

settings = get_settings()

# 2) Modellarni aniq yuklash (metadata to'lsin)
#    Agar sizda app.models paketi bo'lsa, hammasini dinamika bilan import qilamiz:
import app.models as models_pkg

for m in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module(f"{models_pkg.__name__}.{m.name}")

# Alembic config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata
target_metadata = SQLModel.metadata


# (Ixtiyoriy) Constraint/index nomlari uchun konvensiya
# from sqlalchemy import MetaData
# naming_convention = {
#     "ix": "ix_%(column_0_label)s",
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(constraint_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }
# target_metadata = MetaData(naming_convention=naming_convention)

def _get_url() -> str:
    # .env ustun bo'lsin; bo'lmasa alembic.ini dagi "sqlalchemy.url" dan olamiz
    return settings.DATABASE_URL or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Offline mode."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # SQLite uchun muhim
        # include_schemas=True,           # agar public dan tashqari schema ishlatsangiz
        # version_table_schema="public",  # Postgresda version jadvali qayerda saqlansin
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online mode."""
    # Ini ichidagi sozlamalarni olib, URLni dinamik almashtiramiz
    ini_section = config.get_section(config.config_ini_section, {})
    ini_section["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  # SQLite uchun muhim
            # include_schemas=True,
            # version_table_schema="public",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
