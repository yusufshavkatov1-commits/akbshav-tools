from alembic import op

revision = "0004_runtime_hardening"
down_revision = "0003_production_completion"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    statements = [
        "CREATE TABLE IF NOT EXISTS app_user_states (user_id BIGINT PRIMARY KEY REFERENCES app_users(telegram_id) ON DELETE CASCADE,state TEXT NOT NULL,data JSONB NOT NULL DEFAULT '{}'::jsonb,expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE INDEX IF NOT EXISTS idx_user_states_expiry ON app_user_states(expires_at)",
        "CREATE TABLE IF NOT EXISTS app_admin_states (admin_id BIGINT PRIMARY KEY REFERENCES app_admins(telegram_id) ON DELETE CASCADE,state TEXT NOT NULL,data JSONB NOT NULL DEFAULT '{}'::jsonb,expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '15 minutes'),updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
        "CREATE INDEX IF NOT EXISTS idx_admin_states_expiry ON app_admin_states(expires_at)",
        "CREATE TABLE IF NOT EXISTS app_function_registry (key TEXT PRIMARY KEY,name TEXT NOT NULL,category TEXT NOT NULL,version TEXT NOT NULL DEFAULT '1.0.0',enabled BOOLEAN NOT NULL DEFAULT TRUE,description TEXT NOT NULL DEFAULT '')",
    ]
    for sql in statements: bind.exec_driver_sql(sql)

def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled.")
