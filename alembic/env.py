from logging.config import fileConfig
import os
import asyncio
from pathlib import Path
import sys

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Import database models
from src.models.base import Base
import src.models

# Alembic configuration
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Read database URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found in .env file")

config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()