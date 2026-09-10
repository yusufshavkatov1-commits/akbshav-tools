# Pre-host audit — AKBSHAV TOOLS

## Result

**STAGING READY: YES. 100% CLIENT/PRODUCTION READY: NO until live Render + PostgreSQL + Telegram E2E smoke passes.**

This is an honest engineering boundary: static tests can prove syntax, AST, callback coverage and configuration structure, but cannot prove Telegram permissions, Bot API behavior, database connectivity or Render networking without the real environment.

## Fixed in this release

- Fixed standalone `run_user_bot.py` / `run_admin_bot.py` launchers: they no longer call `asyncio.run()` around synchronous `run_polling()`.
- Added persistent PostgreSQL user/admin state with expiry for support, search, broadcast and login flows; no critical FSM state is kept only in Python memory.
- Added `ADMIN_OWNER_ID`; only that configured ID receives the owner role on first registration. Other allowlisted IDs become admins.
- Added backend function registry seeding during FastAPI startup. This is important because PTB `post_init` is not relied upon when applications are started manually by the FastAPI lifespan.
- Removed the in-memory auto-reply cooldown dependency; cooldown is claimed atomically in PostgreSQL.
- Added idempotent broadcast delivery records so a worker crash does not blindly resend already delivered users.
- Added global Telegram error handlers with internal error recording and safe user-facing errors.
- Added callback length and numeric-payload validation.
- Added persistent quick-reply save/remove commands.
- Added function registry metadata and backend feature state.
- Added migration 0004 for runtime state/registry and 0005 for broadcast idempotency.

## Verified locally

- `python -m compileall -q .` — PASS
- AST parse of all Python files — PASS
- `python tests_smoke.py` — PASS
- localization parity — PASS, 35 keys × 3 languages
- function/stub audit — PASS
- callback/button audit — PASS
- static security audit — PASS
- ZIP integrity — PASS

## Cannot be truthfully verified in this environment

The current environment does not have `python-telegram-bot` or `asyncpg` installed and has no usable package-network access. Therefore a real import/startup test against Telegram and PostgreSQL was not possible here.

Before taking paying clients, run the staging checklist in README against real Render + PostgreSQL/Supabase and two real Telegram bots.

## Intentionally partial

The project does **not** expose fake buttons for capabilities that are not implemented. Full media/video/audio engines, arbitrary automation graphs, exhaustive moderation, full profile-management suite and a complete admin translation editor remain partial/unavailable in this release.
