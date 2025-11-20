"""add appointments table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "2024070404"
down_revision = "516a09494af5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False, server_default="in_person"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_channels", sa.JSON(), nullable=True),
        sa.Column("reminder_task_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_appointments_user_start", "appointments", ["user_id", "start_at"])
    op.create_index("ix_appointments_customer", "appointments", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_appointments_customer", table_name="appointments")
    op.drop_index("ix_appointments_user_start", table_name="appointments")
    op.drop_table("appointments")
