"""add invoices table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "2024070407"
down_revision = "2024070406"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("number", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="TRY"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_invoices_user", "invoices", ["user_id"])
    op.create_unique_constraint("uq_invoices_number", "invoices", ["number"])


def downgrade() -> None:
    op.drop_constraint("uq_invoices_number", "invoices", type_="unique")
    op.drop_index("ix_invoices_user", table_name="invoices")
    op.drop_table("invoices")
