# Risk List — Phase 0

## Critical

- Polling instead of webhook production architecture.
- No durable job recovery.
- No Alembic migrations.
- No complete RBAC.
- Broadcast can block and has no durable cancellation/recovery.
- Event worker can duplicate notifications under concurrency.
- Missing file/media security because media engine is absent.
- Missing rate limiting.
- Missing admin brute-force controls.
- Missing security/audit infrastructure.
- Missing localization parity guarantees.

## High

- Hardcoded user/admin strings.
- In-memory auto-reply cooldown.
- Import-time environment failure.
- No proper health/readiness endpoints.
- No comprehensive test matrix.
- No persistent library/automation model.
- No backup/restore operational procedure.

## Medium

- Search/list UX is basic.
- Ticket states are too limited.
- Usage analytics are minimal.
- README does not describe a complete production deployment.

## External dependency risk

Telegram Business capabilities are permission- and API-version-dependent. The implementation must verify actual Bot API/PTB support per operation and never expose unsupported functions as working. citeturn0search0turn0search3
