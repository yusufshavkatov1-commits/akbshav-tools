from __future__ import annotations

import json
from contextlib import asynccontextmanager
from typing import Any

import asyncpg

from common.config import DATABASE_URL

pool: asyncpg.Pool | None = None


async def init_db() -> None:
    global pool
    if pool is not None:
        return
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=30,
        max_inactive_connection_lifetime=300,
        server_settings={"application_name": "akbshav_tools"},
    )


async def close_db() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


@asynccontextmanager
async def connection():
    if pool is None:
        raise RuntimeError("Database is not initialized")
    async with pool.acquire() as conn:
        yield conn


async def execute(query: str, *args: Any):
    async with connection() as conn:
        return await conn.execute(query, *args)


async def fetchrow(query: str, *args: Any):
    async with connection() as conn:
        return await conn.fetchrow(query, *args)


async def fetch(query: str, *args: Any):
    async with connection() as conn:
        return await conn.fetch(query, *args)


async def fetchval(query: str, *args: Any):
    async with connection() as conn:
        return await conn.fetchval(query, *args)


async def rate_limit(user_id: int, bucket: str, limit: int, window_seconds: int = 60) -> bool:
    """Atomic fixed-window limiter. Returns True when the request is allowed."""
    async with connection() as conn:
        row = await conn.fetchrow(
            """INSERT INTO app_rate_limits(user_id,bucket,window_started_at,count)
               VALUES($1,$2,NOW(),1)
               ON CONFLICT(user_id,bucket) DO UPDATE
               SET count=CASE WHEN app_rate_limits.window_started_at <= NOW() - ($3 * INTERVAL '1 second') THEN 1 ELSE app_rate_limits.count + 1 END,
                   window_started_at=CASE WHEN app_rate_limits.window_started_at <= NOW() - ($3 * INTERVAL '1 second') THEN NOW() ELSE app_rate_limits.window_started_at END
               RETURNING count""", user_id, bucket, window_seconds
        )
        return int(row["count"]) <= limit


async def insert_security_event(user_id: int | None, event_type: str, severity: str = "info", details: dict[str, Any] | None = None) -> None:
    await execute(
        "INSERT INTO app_security_events(user_id,event_type,severity,details) VALUES($1,$2,$3,$4::jsonb)",
        user_id, event_type, severity, json.dumps(details or {}, ensure_ascii=False),
    )


async def insert_function_error(user_id: int | None, function_key: str, error_code: str, details: dict[str, Any] | None = None) -> None:
    await execute(
        "INSERT INTO app_function_errors(user_id,function_key,error_code,details) VALUES($1,$2,$3,$4::jsonb)",
        user_id, function_key, error_code, json.dumps(details or {}, ensure_ascii=False),
    )


async def insert_event(event_type: str, payload: dict[str, Any]) -> None:
    await execute(
        "INSERT INTO app_events(event_type,payload) VALUES($1,$2::jsonb)",
        event_type,
        json.dumps(payload, ensure_ascii=False),
    )


async def set_state(table: str, owner_column: str, owner_id: int, state: str, data: dict[str, Any] | None = None, minutes: int = 30) -> None:
    if table not in {"app_user_states", "app_admin_states"} or owner_column not in {"user_id", "admin_id"}:
        raise ValueError("invalid state storage")
    await execute(
        f"INSERT INTO {table}({owner_column},state,data,expires_at) VALUES($1,$2,$3::jsonb,NOW()+($4 * INTERVAL '1 minute')) ON CONFLICT({owner_column}) DO UPDATE SET state=$2,data=$3::jsonb,expires_at=NOW()+($4 * INTERVAL '1 minute'),updated_at=NOW()",
        owner_id, state, json.dumps(data or {}, ensure_ascii=False), minutes,
    )


async def get_state(table: str, owner_column: str, owner_id: int) -> tuple[str, dict[str, Any]] | None:
    if table not in {"app_user_states", "app_admin_states"} or owner_column not in {"user_id", "admin_id"}:
        raise ValueError("invalid state storage")
    row = await fetchrow(f"SELECT state,data FROM {table} WHERE {owner_column}=$1 AND expires_at>NOW()", owner_id)
    if not row:
        await execute(f"DELETE FROM {table} WHERE {owner_column}=$1", owner_id)
        return None
    return str(row["state"]), dict(row["data"] or {})


async def clear_state(table: str, owner_column: str, owner_id: int) -> None:
    if table not in {"app_user_states", "app_admin_states"} or owner_column not in {"user_id", "admin_id"}:
        raise ValueError("invalid state storage")
    await execute(f"DELETE FROM {table} WHERE {owner_column}=$1", owner_id)
