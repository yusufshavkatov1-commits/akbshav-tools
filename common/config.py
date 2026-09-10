from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _int_set(name: str) -> set[int]:
    out: set[int] = set()
    for value in _env(name).split(","):
        value = value.strip()
        if value:
            try:
                out.add(int(value))
            except ValueError as exc:
                raise RuntimeError(f"{name} contains a non-integer value") from exc
    return out

USER_BOT_TOKEN = _env("USER_BOT_TOKEN")
ADMIN_BOT_TOKEN = _env("ADMIN_BOT_TOKEN")
DATABASE_URL = _env("DATABASE_URL")
REQUIRED_CHANNEL = _env("REQUIRED_CHANNEL", "@akbshav_channel")
BOT_USERNAME = _env("BOT_USERNAME", "AKBSHAVTOOLS_bot").lstrip("@")
ADMIN_IDS = _int_set("ADMIN_IDS")
ADMIN_OWNER_ID = int(_env("ADMIN_OWNER_ID", str(next(iter(sorted(ADMIN_IDS)), 0)))) if ADMIN_IDS else 0
APP_VERSION = _env("APP_VERSION", "3.0.0")
RATE_LIMIT_PER_MINUTE = max(1, int(_env("RATE_LIMIT_PER_MINUTE", "30")))
BROADCAST_BATCH_SIZE = max(1, int(_env("BROADCAST_BATCH_SIZE", "25")))
JOB_MAX_ATTEMPTS = max(1, int(_env("JOB_MAX_ATTEMPTS", "5")))
ADMIN_PASSWORD = _env("ADMIN_PASSWORD")
ADMIN_PASSWORD_HASH = _env("ADMIN_PASSWORD_HASH")
COMMAND_PREFIX = _env("COMMAND_PREFIX", ".")[:1] or "."
SESSION_HOURS = int(_env("ADMIN_SESSION_HOURS", "12"))
# Backward-compatible name used by admin_bot.
ADMIN_SESSION_HOURS = SESSION_HOURS
MAX_REPEATS = int(_env("MAX_REPEATS", "20"))
MAX_WORDS = int(_env("MAX_WORDS", "30"))
MAX_MESSAGE_LENGTH = int(_env("MAX_MESSAGE_LENGTH", "3500"))
AUTO_REPLY_COOLDOWN = float(_env("AUTO_REPLY_COOLDOWN", "8"))
WEBHOOK_URL = _env("WEBHOOK_URL").rstrip("/")
WEBHOOK_SECRET = _env("WEBHOOK_SECRET")
WEB_PORT = int(_env("PORT", "10000"))
ENVIRONMENT = _env("ENVIRONMENT", "development").lower()


def validate_runtime(*, production: bool | None = None) -> None:
    production = ENVIRONMENT == "production" if production is None else production
    required = {"USER_BOT_TOKEN": USER_BOT_TOKEN, "ADMIN_BOT_TOKEN": ADMIN_BOT_TOKEN, "DATABASE_URL": DATABASE_URL}
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing required environment variable(s): " + ", ".join(missing))
    if not ADMIN_IDS:
        raise RuntimeError("ADMIN_IDS must contain at least one Telegram user ID")
    if ADMIN_OWNER_ID and ADMIN_OWNER_ID not in ADMIN_IDS:
        raise RuntimeError("ADMIN_OWNER_ID must be included in ADMIN_IDS")
    if not ADMIN_PASSWORD and not ADMIN_PASSWORD_HASH:
        raise RuntimeError("Set ADMIN_PASSWORD_HASH (recommended) or ADMIN_PASSWORD")
    if production and (not WEBHOOK_URL or not WEBHOOK_SECRET):
        raise RuntimeError("Production requires WEBHOOK_URL and WEBHOOK_SECRET")
