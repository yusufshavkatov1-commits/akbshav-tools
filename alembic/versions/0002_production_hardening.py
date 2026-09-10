from alembic import op

revision = "0002_production_hardening"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    statements = [
        "ALTER TABLE app_users ADD COLUMN IF NOT EXISTS strikes INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE app_business_connections ADD COLUMN IF NOT EXISTS rights_json JSONB NOT NULL DEFAULT '{}'::jsonb",
        "ALTER TABLE app_admins ADD COLUMN IF NOT EXISTS enabled BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE app_admin_sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
        "ALTER TABLE app_tickets ADD COLUMN IF NOT EXISTS topic TEXT NOT NULL DEFAULT 'other'",
        "ALTER TABLE app_tickets ADD COLUMN IF NOT EXISTS assigned_admin_id BIGINT",
        "ALTER TABLE app_tickets ADD COLUMN IF NOT EXISTS unread_user INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE app_tickets ADD COLUMN IF NOT EXISTS unread_admin INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE app_auto_replies ADD COLUMN IF NOT EXISTS last_reply_at TIMESTAMPTZ",
        "ALTER TABLE app_tickets DROP CONSTRAINT IF EXISTS app_tickets_status_check",
        "UPDATE app_tickets SET status='in_progress' WHERE status='open'",
        "ALTER TABLE app_tickets ADD CONSTRAINT app_tickets_status_check CHECK(status IN ('new','in_progress','answered','waiting_user','closed','rejected'))",
    ]
    for statement in statements:
        bind.exec_driver_sql(statement)
    with open("db/schema.sql", encoding="utf-8") as fh:
        sql = fh.read()
    for statement in sql.split(";\n"):
        statement = statement.strip()
        if statement and ("CREATE TABLE IF NOT EXISTS app_admin_permissions" in statement
                          or "CREATE TABLE IF NOT EXISTS app_admin_logins" in statement
                          or "CREATE TABLE IF NOT EXISTS app_admin_actions" in statement
                          or "CREATE TABLE IF NOT EXISTS app_ticket_ratings" in statement
                          or "CREATE TABLE IF NOT EXISTS app_jobs" in statement
                          or "CREATE TABLE IF NOT EXISTS app_broadcasts" in statement):
            bind.exec_driver_sql(statement)


def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled.")
