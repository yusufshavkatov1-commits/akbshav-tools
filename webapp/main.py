from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from telegram import Update

from common.config import (
    WEBHOOK_SECRET, WEBHOOK_URL, WEB_PORT, USER_BOT_TOKEN, ADMIN_BOT_TOKEN,
    validate_runtime,
)
from db.database import close_db, init_db, fetchval
from user_bot.main import build_app as build_user_app, seed_registry
from admin_bot.main import build_app as build_admin_app

log = logging.getLogger("akbshav.web")


async def _start_ptb(application):
    await application.initialize()
    await application.start()
    return application


async def _stop_ptb(application):
    await application.stop()
    await application.shutdown()


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime()
    await init_db()
    await seed_registry()
    user_app = build_user_app()
    admin_app = build_admin_app()
    await _start_ptb(user_app)
    await _start_ptb(admin_app)
    app.state.user_bot = user_app
    app.state.admin_bot = admin_app

    if WEBHOOK_URL and WEBHOOK_SECRET:
        await user_app.bot.set_webhook(
            f"{WEBHOOK_URL}/webhook/user",
            secret_token=WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query", "business_connection", "business_message", "edited_business_message", "deleted_business_messages"],
            drop_pending_updates=False,
        )
        user_webhook_url = f"{WEBHOOK_URL}/webhook/user"
        admin_webhook_url = f"{WEBHOOK_URL}/webhook/admin"
        await user_app.bot.set_webhook(
            user_webhook_url,
            secret_token=WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query", "business_connection", "business_message", "edited_business_message", "deleted_business_messages"],
            drop_pending_updates=False,
        )
        await admin_app.bot.set_webhook(
            admin_webhook_url,
            secret_token=WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,
        )
        user_me = await user_app.bot.get_me()
        admin_me = await admin_app.bot.get_me()
        user_info = await user_app.bot.get_webhook_info()
        admin_info = await admin_app.bot.get_webhook_info()
        log.info(
            "User bot configured: @%s | webhook=%s | pending=%s | last_error=%s",
            user_me.username, user_info.url, user_info.pending_update_count, user_info.last_error_message or "none",
        )
        log.info(
            "Admin bot configured: @%s | webhook=%s | pending=%s | last_error=%s",
            admin_me.username, admin_info.url, admin_info.pending_update_count, admin_info.last_error_message or "none",
        )
        log.info("Telegram webhooks configured")
    try:
        yield
    finally:
        if WEBHOOK_URL and WEBHOOK_SECRET:
            for bot in (user_app.bot, admin_app.bot):
                try:
                    await bot.delete_webhook(drop_pending_updates=False)
                except Exception:
                    log.exception("Failed to remove webhook")
        await _stop_ptb(admin_app)
        await _stop_ptb(user_app)
        await close_db()


app = FastAPI(title="AKBSHAV TOOLS", version="2.0.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {"service": "AKBSHAV TOOLS", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": __import__("common.config", fromlist=["APP_VERSION"]).APP_VERSION}


@app.get("/ready")
async def ready():
    if not hasattr(app.state, "user_bot"):
        raise HTTPException(status_code=503, detail="service not ready")
    try:
        await fetchval("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="database not ready")
    return {"status": "ready"}


async def _handle_webhook(request: Request, application, secret: str | None):
    received = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret and received != secret:
        raise HTTPException(status_code=403, detail="forbidden")
    try:
        log.info("Telegram webhook received: path=%s", request.url.path)
        if int(request.headers.get("content-length", "0") or 0) > 2_000_000:
            raise HTTPException(status_code=413, detail="payload too large")
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("invalid JSON object")
        update = Update.de_json(payload, application.bot)
        if update is None:
            raise ValueError("invalid update")
        await application.process_update(update)
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid update")
    except Exception:
        log.exception("Telegram update processing failed")
        raise HTTPException(status_code=500, detail="update processing failed")
    return {"ok": True}


@app.post("/webhook/user")
async def user_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    return await _handle_webhook(request, app.state.user_bot, WEBHOOK_SECRET)


@app.post("/webhook/admin")
async def admin_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    return await _handle_webhook(request, app.state.admin_bot, WEBHOOK_SECRET)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webapp.main:app", host="0.0.0.0", port=WEB_PORT)
