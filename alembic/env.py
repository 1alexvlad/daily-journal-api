# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database import Base
from app.config import settings
from app.models import Note
from app.users.models import User

config = context.config

config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

print(f"Таблицы в метаданных: {list(target_metadata.tables.keys())}")


def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Выполнение миграций"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True, 
        render_as_batch=True, 
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    """Асинхронный запуск миграций"""
    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            poolclass=pool.NullPool,
        )
        async with engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
    except Exception as e:
        print(f"Ошибка при выполнении миграций: {e}")
        raise
    finally:
        await engine.dispose()

def run_migrations_online() -> None:
    """Запуск асинхронных миграций"""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()