# Database Gap — Phase 0

## Existing tables

- app_users
- app_business_connections
- app_admins
- app_admin_sessions
- app_tickets
- app_ticket_messages
- app_functions
- app_settings
- app_events
- app_message_archive
- app_quick_replies
- app_auto_replies
- app_usage

## Required major additions

users/user_settings/languages/rules/rules_acceptance/channels/subscriptions/business_connections/functions/function_settings/function_usage/function_errors/admins/admin_sessions/admin_logs/tickets/ticket_messages/broadcasts/broadcast_jobs/library/saved_replies/saved_voice/saved_gifs/profiles/automations/automation_rules/automation_runs/scheduled_messages/scheduled_tasks/deleted_messages/edited_messages/media_objects/jobs/job_attempts/rate_limits/notifications/localization_strings/user_restrictions/blacklist/whitelist.

## Migration requirements

Replace startup `schema.sql` creation with Alembic migrations. Startup must never reset or destructively recreate production state.

## Concurrency requirements

Use unique constraints/idempotency keys for webhook/job/event processing. Event delivery must claim rows atomically before sending to avoid duplicate delivery across multiple processes.
