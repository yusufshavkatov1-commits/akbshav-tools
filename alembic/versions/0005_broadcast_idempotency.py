from alembic import op
revision="0005_broadcast_idempotency"
down_revision="0004_runtime_hardening"
branch_labels=None
depends_on=None
def upgrade():
    op.get_bind().exec_driver_sql("CREATE TABLE IF NOT EXISTS app_broadcast_deliveries (broadcast_id BIGINT NOT NULL REFERENCES app_broadcasts(id) ON DELETE CASCADE,user_id BIGINT NOT NULL REFERENCES app_users(telegram_id) ON DELETE CASCADE,status TEXT NOT NULL CHECK(status IN ('sent','failed')),error TEXT,sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),PRIMARY KEY(broadcast_id,user_id))")
    op.get_bind().exec_driver_sql("CREATE INDEX IF NOT EXISTS idx_broadcast_deliveries_status ON app_broadcast_deliveries(broadcast_id,status)")
def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled.")
