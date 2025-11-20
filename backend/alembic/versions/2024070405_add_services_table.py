"""add services table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "2024070405"
down_revision = "2024070404"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("price_amount", sa.Float(), nullable=False),
        sa.Column("price_currency", sa.String(length=10), nullable=False, server_default="TRY"),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_services_user", "services", ["user_id"])
    op.create_index("ix_services_status", "services", ["status"])


def downgrade() -> None:
    op.drop_index("ix_services_status", table_name="services")
    op.drop_index("ix_services_user", table_name="services")
    op.drop_table("services")
