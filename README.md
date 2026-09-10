# AKBSHAV TOOLS — Production Hardened Release

## What this package actually is

A production-oriented Telegram Business utility service with:

- separate USER and ADMIN bots;
- FastAPI webhook service;
- PostgreSQL/asyncpg persistence;
- Alembic migrations;
- durable PostgreSQL worker queue;
- Telegram Business connection/message/edit/delete handling;
- RU / UZ / EN user onboarding and UI catalog;
- required-channel gate;
- feature flags enforced in backend;
- controlled text tools and Business auto-reply;
- support tickets;
- admin authentication, RBAC and audit log;
- analytics based on real PostgreSQL data;
- scheduled/cancellable broadcast jobs;
- security/rate-limit events;
- Render web + worker deployment.

This release deliberately does **not** expose unsupported/fake features.

## Telegram Business capability boundary

The project uses Bot API Business updates and `business_connection_id` for supported actions. It stores Business rights and refuses outbound Business replies when the connection is disabled or explicitly lacks `can_reply`.

Telegram can notify a bot about deleted Business messages, but the deletion update contains message IDs rather than the original message content. Archived content can therefore be marked deleted, not reconstructed if it was never received.

## Architecture

```text
Telegram
  │
  ├── USER BOT ──┐
  └── ADMIN BOT ─┼── FastAPI / webhook
                 │
                 ├── PostgreSQL (persistent state)
                 └── Worker (durable jobs / broadcasts)
```

Render local filesystem is never treated as durable application state.

## Environment

Copy `.env.example` to `.env` for local development. Production secrets belong in Render Environment Variables.

Required:

- `USER_BOT_TOKEN`
- `ADMIN_BOT_TOKEN`
- `DATABASE_URL`
- `ADMIN_IDS`
- `ADMIN_PASSWORD_HASH` (preferred) or `ADMIN_PASSWORD`
- `WEBHOOK_URL`
- `WEBHOOK_SECRET`

See `.env.example` for optional limits and versioning.

## Local checks

```bash
python -m compileall -q .
python tests_smoke.py
python scripts/audit_localization.py
python scripts/audit_functions.py
python scripts/audit_buttons.py
python scripts/security_check.py
```

Database-dependent health check:

```bash
python scripts/health_check.py
```

## Migrations

```bash
alembic upgrade head
```

Current chain:

`0001_initial → 0002_production_hardening → 0003_production_completion → 0004_runtime_hardening → 0005_broadcast_idempotency`

## Run locally

Web service:

```bash
python run.py
```

Worker:

```bash
python worker.py
```

For production, use the webhook service rather than polling.

## Render

`render.yaml` defines:

1. Web service — FastAPI + both Telegram applications.
2. Worker — durable PostgreSQL job processor.

The worker is important for delayed Business messages and scheduled broadcasts. A sleeping Render Free service cannot provide 24/7 monitoring; external uptime/monitoring should be used if continuous availability is required.

## Admin

The Admin Bot uses:

- Telegram ID allowlist;
- PBKDF2 password hash support;
- expiring sessions;
- failed-login throttling;
- role/permission checks on backend actions;
- audit records for privileged actions.

Roles currently supported: `owner`, `admin`, `moderator`. Additional permissions can be stored in `app_admin_permissions`.

## Broadcasts

Broadcasts are persisted before execution. The Admin Bot supports:

- queueing an immediate broadcast;
- scheduling by ISO timestamp;
- scheduled list;
- history;
- cancellation;
- sent/failed counters.

The worker claims jobs with PostgreSQL row locks and recovers abandoned jobs after a timeout.

## Honest scope note

This archive is a hardened working release, not a claim that every aspirational item in the supplied Master Prompt exists. Advanced media/voice processing, a full drag-and-drop automation builder, complete privacy center, exhaustive moderation suite and full admin translation editor are intentionally not represented as finished features.


## Pre-host gate

Deploy to staging first. Do not advertise unsupported features as available.

1. Set all Render environment variables, including `ADMIN_OWNER_ID`.
2. Run `alembic upgrade head` and confirm all migrations succeed.
3. Open `/health` and `/ready`; `/ready` must return HTTP 200.
4. Test USER `/start` → language → rules → required channel → main menu.
5. Test repeated `/start`; the onboarding state must be recovered from PostgreSQL.
6. Connect a Telegram Business account and verify `connected` / `disconnected` events.
7. Send a Business message and test archive, `.reverse`, `.repeat`, `.timer`, `.autoreply`, `.save`, `.unsave`.
8. Test that removing `can_reply` prevents outbound Business replies instead of pretending success.
9. Test support ticket creation and Admin Bot reply.
10. Test admin login, owner/admin separation, function toggle and audit log.
11. Send a broadcast to test users only; verify delivery records and retry behavior.
12. Restart the web service and worker; verify users, tickets, connections, jobs and broadcasts remain in PostgreSQL.
13. Check Render logs for startup errors and Telegram webhook errors.

Only after this checklist passes should the release be used with paying clients.
