# Implemented Function Inventory

This release intentionally documents only functionality that is actually wired to backend code.

## User / Business
- onboarding, language selection, rules acceptance, required-channel verification
- Telegram Business connection lifecycle
- Business message archive and edit/delete tracking
- controlled text commands: help, reverse, nospace, bubble, leet, dumb, glitch, spoiler, words, heart, print, matrix, coin, repeat, quote
- PostgreSQL-backed auto-reply with cooldown
- PostgreSQL-backed delayed Business message jobs
- quick-reply lookup
- support ticket creation
- feature flags enforced by backend
- per-user Business message rate limiting and security events

## Admin
- allowlist + password authentication
- PBKDF2 password hash support
- expiring admin sessions
- failed-login throttling
- RBAC roles: owner/admin/moderator + explicit permissions
- user search, profile, block/unblock
- ticket list, reply, close
- function enable/disable
- analytics: total, DAU, WAU, MAU, D1 retention, languages, errors, Business connections
- broadcast queue, scheduling, history and cancellation
- audit log
- system queue counters

## Worker
- durable PostgreSQL job queue
- SKIP LOCKED job claiming
- abandoned-job recovery
- exponential retry/backoff with bounded attempts
- delayed Business messages
- batched broadcasts with progress counters

## Deliberately not exposed as fake buttons
Advanced media processing, arbitrary profile changes, unrestricted moderation, full automation builder, account takedown, doxxing/PII lookup and other functions that require capabilities not implemented in this package are not advertised as available.
