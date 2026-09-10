from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # The canonical schema is intentionally kept in db/schema.sql for portability.
    # Render runs this migration before services; the SQL is idempotent.
    bind = op.get_bind()
    with open("db/schema.sql", encoding="utf-8") as fh:
        for statement in fh.read().split(";\n"):
            statement = statement.strip()
            if statement:
                bind.exec_driver_sql(statement)


def downgrade():
    raise RuntimeError("Destructive downgrade is intentionally disabled; use a reviewed backup/restore procedure.")
