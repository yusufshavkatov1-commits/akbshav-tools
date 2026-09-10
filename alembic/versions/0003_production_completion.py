from alembic import op

revision = "0003_production_completion"
down_revision = "0002_production_hardening"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    statements = [
        "CREATE TABLE IF NOT EXISTS app_security_events (id BIGSERIAL PRIMARY KEY,user_id BIGINT,event_type TEXT NOT NULL,severity TEXT NOT NULL DEFAULT 'info',details JSONB NOT NULL DEFAULT '{}'::jsonb,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE INDEX IF NOT EXISTS idx_security_events_created ON app_security_events(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_security_events_user ON app_security_events(user_id,created_at DESC)",
        "CREATE TABLE IF NOT EXISTS app_function_errors (id BIGSERIAL PRIMARY KEY,user_id BIGINT,function_key TEXT NOT NULL,error_code TEXT NOT NULL,details JSONB NOT NULL DEFAULT '{}'::jsonb,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE INDEX IF NOT EXISTS idx_function_errors_created ON app_function_errors(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_function_errors_function ON app_function_errors(function_key,created_at DESC)",
        "CREATE TABLE IF NOT EXISTS app_localization_strings (language TEXT NOT NULL CHECK(language IN ('ru','uz','en')),key TEXT NOT NULL,value TEXT NOT NULL,updated_by BIGINT,updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),PRIMARY KEY(language,key))",
        "CREATE TABLE IF NOT EXISTS app_promotion_events (id BIGSERIAL PRIMARY KEY,user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,event_type TEXT NOT NULL CHECK(event_type IN ('shown','continued','subscribed')),created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE INDEX IF NOT EXISTS idx_promotion_events ON app_promotion_events(event_type,created_at DESC)",
        "CREATE TABLE IF NOT EXISTS app_rate_limits (user_id BIGINT NOT NULL,bucket TEXT NOT NULL,window_started_at TIMESTAMPTZ NOT NULL,count INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(user_id,bucket))",
        "ALTER TABLE app_message_archive ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ",
        "ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ",
        "ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ",
        "ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS targeted INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS language TEXT",
        "ALTER TABLE app_broadcasts ADD COLUMN IF NOT EXISTS active_only BOOLEAN NOT NULL DEFAULT FALSE",
        "CREATE INDEX IF NOT EXISTS idx_broadcasts_scheduled ON app_broadcasts(status,scheduled_at)",
    ]
    for sql in statements:
        bind.exec_driver_sql(sql)

def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled; restore from backup if rollback is required.")
