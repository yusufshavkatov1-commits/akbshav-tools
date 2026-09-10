from __future__ import annotations

import asyncio
from logging.config import fileConfig
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from common.config import DATABASE_URL

# Normalize PostgreSQL URL for asyncpg.
DATABASE_URL = DATABASE_URL.replace("sslmode=", "ssl=")


def sqlalchemy_database_url(url: str) -> str:
    """Convert a PostgreSQL URL to the SQLAlchemy asyncpg-compatible form.

    Cloud PostgreSQL providers commonly expose ``sslmode=require`` in their
    connection URL. SQLAlchemy's asyncpg dialect forwards query parameters
    directly to asyncpg.connect(), where the equivalent keyword is ``ssl``.
    """
    if not url:
        return url
    parts = urlsplit(url)
    scheme = parts.scheme
    if scheme == "postgresql":
        scheme = "postgresql+asyncpg"
    elif scheme == "postgres":
        scheme = "postgresql+asyncpg"
    query = parse_qsl(parts.query, keep_blank_values=True)
    normalized = []
    ssl_present = any(key == "ssl" for key, _ in query)
    for key, value in query:
        if key == "sslmode":
            if not ssl_present:
                normalized.append(("ssl", value))
        else:
            normalized.append((key, value))
    return urlunsplit((scheme, parts.netloc, parts.path, urlencode(normalized), parts.fragment))


config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", sqlalchemy_database_url(DATABASE_URL))


def run_migrations_offline() -> None:
    context.configure(url=DATABASE_URL, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
