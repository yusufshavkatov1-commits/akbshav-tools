# Phase 0 — Production Audit

Date: 2026-09-10
Source archive: akbshav_tools_full.zip
Reference specification: TELEGRAM TOOLS PRO Master Prompt

## Executive result

The supplied archive is a small production-oriented prototype, not a production-ready implementation of the Master Prompt.

The archive contains 9 Python source modules and a small PostgreSQL schema. It does **not** contain the two MP4 competitor recordings described by the Master Prompt, so competitor-video analysis cannot be truthfully completed from this archive.

Syntax compilation passes, but the project fails the Master Prompt quality gate because major required subsystems are absent: FastAPI/webhook service, Alembic migrations, job persistence/recovery, full RBAC, function registry/specs, localization audit, function/button audits, library, automation engine, analytics, robust broadcast queue, security event system, privacy center, media/file engines, and comprehensive tests.

## Current strengths

- Python 3 code compiles successfully.
- python-telegram-bot 22.8 is pinned.
- PostgreSQL/asyncpg is used instead of SQLite.
- BusinessConnection, business_message, edited_business_message and deleted_business_messages are wired in the user bot.
- SQL parameters are used for database values.
- User onboarding includes language, rules acceptance and required-channel checking.
- Admin bot is separated from the user bot.
- Password hashing utility exists and PBKDF2 verification is implemented.
- Basic feature toggles and usage tracking exist.
- Basic ticket, broadcast, user block and statistics functions exist.
- Safety exclusions for mass spam, doxxing and account destruction are documented.

## Blocking findings

1. No competitor MP4 files are present in the supplied ZIP; video benchmark analysis is therefore pending.
2. `common/config.py` raises at import time when environment variables are absent, making ordinary local imports/smoke tests fail without a complete production environment.
3. No FastAPI application or public webhook endpoint exists.
4. Both bots use `run_polling()`; the Master Prompt explicitly targets webhook architecture for production.
5. `render.yaml` deploys two workers, but no web service exists for webhook/health endpoints.
6. `db/schema.sql` is executed directly at startup. There is no Alembic migration system.
7. `schema.sql` is not a complete model for the Master Prompt and has no migration history.
8. Important scheduled state is held in PTB JobQueue (`.timer`) rather than PostgreSQL-backed jobs; it is therefore lost on restart.
9. `LAST_AUTO_REPLY` is an in-memory dictionary; cooldown state is not shared between instances and is lost on restart.
10. `app_events` delivery has a race: rows are read and marked delivered after sending without an atomic claim/lock, so multiple workers can send duplicate admin notifications.
11. Admin authorization is primarily an ID allowlist plus a session. The schema has roles but callback actions do not enforce fine-grained RBAC permissions.
12. Any admin session can execute user block, ticket close, broadcast, function toggle and event access; there is no OWNER/ADMIN/MODERATOR/SUPPORT permission matrix.
13. Broadcast is synchronous and unqueued. A large user list blocks the admin handler and has no durable job, preview, audience selection, confirmation or cancellation workflow.
14. Ticket system only has `open/closed`; required states, assignment/claim, priority, reopen, unread counters, full support workflow and rating are missing.
15. User-facing close/reopen semantics do not match the requested support model.
16. Localization is hardcoded in Python and contains non-localized strings in handlers/features/admin UI. There is no runtime-editable localization store or localization audit.
17. The command help explicitly says QR will be added later. This is a dead/placeholder promise and violates the no-fake/no-placeholder rule.
18. There is a `pass` statement in `admin_bot/main.py` inside an exception path, violating the project's no-pass production requirement.
19. `__pycache__`/`.pyc` files are shipped in the ZIP.
20. There are no real unit/integration/security/localization/button/function audit suites; only a small smoke test exists.
21. No persistent library model exists beyond quick replies.
22. No automation rule engine exists; only a simple per-user auto-reply exists.
23. No media/voice/file processing engine exists despite the Master Prompt requirements.
24. No analytics schema exists for DAU/WAU/MAU/retention/errors/function usage cohorts.
25. No privacy export/delete center exists.
26. No rate-limit tables/service exist.
27. No durable notification service exists.
28. No health/readiness endpoints exist.
29. No structured audit-log model exists for administrative actions.
30. No backup/restore implementation or operational runbook is included.
31. `render.yaml` duplicates both bot tokens into both workers, violating least-privilege secret distribution.
32. Render worker architecture is not sufficient for webhook delivery or health checks. Current Render documentation supports dedicated web services for HTTP/webhooks and background workers for continuous queue processing. citeturn1search0turn1search1

## Telegram capability conclusions

- Telegram Business connections and business message/edit/delete updates are real Bot API capabilities. citeturn0search0turn0search3
- Sending on behalf of a connected Business account is permission-dependent and uses `business_connection_id`; not every operation is universally available. citeturn0search10turn0search3
- Business deletion updates provide message IDs; the archive can preserve content only if that content was previously captured. The deletion update itself is not a complete content snapshot. citeturn0search7
- Webhooks support a Telegram secret token header and are the correct production push mechanism when a public HTTPS endpoint is available. citeturn0search4turn0search2
- Some advanced Business operations are MTProto-level capabilities and require explicit capability verification; they must not be assumed to be available through the simple Bot API wrapper. citeturn0search3

## Render conclusion

A production architecture should use a public web service for Telegram webhooks/health endpoints and separate background workers for durable jobs. Render documents background workers for continuous queue processing and web services for HTTP applications. Free web services also spin down after 15 minutes without inbound traffic, while local filesystem changes are ephemeral; therefore critical state must stay in PostgreSQL/object storage. citeturn1search0turn1search1turn1search3

## Quality gate

Current result: **FAIL**.

The archive is a foundation to rebuild from, not the final project.
