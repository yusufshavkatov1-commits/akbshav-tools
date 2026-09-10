# Final hardening changes

- Added migration `0003_production_completion`.
- Added durable security events, function error records, promotion events and atomic rate limits.
- Added broadcast scheduling/cancellation/history backed by PostgreSQL jobs.
- Added worker crash recovery and bounded exponential retry.
- Added backend RBAC checks for admin actions.
- Added failed-admin-login throttling and audit records.
- Added real analytics: DAU, WAU, MAU, D1 retention, language distribution and error counts.
- Added Business connection rights validation before outbound replies.
- Added deletion markers to archived Business messages.
- Improved `/health` and `/ready` with database readiness checks.
- Added localization parity, function, callback and security audit scripts.
- Improved `/start` so returning users recover their persisted onboarding state.
- Added rate limiting for incoming Business messages.
- Removed stale production-status claims and documented the actual supported scope.
