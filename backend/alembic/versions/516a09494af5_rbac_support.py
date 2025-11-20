"""rbac support - roles tablosu ve fk"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, table

revision = "516a09494af5"
down_revision = "2024070403"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_assignable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    roles_table = table(
        "roles",
        column("slug", sa.String(length=50)),
        column("name", sa.String(length=100)),
        column("description", sa.String(length=255)),
        column("is_assignable", sa.Boolean()),
    )
    op.bulk_insert(
        roles_table,
        [
            {"slug": "owner", "name": "Sahip", "description": "Kurucu/süper kullanıcı", "is_assignable": False},
            {"slug": "admin", "name": "Yönetici", "description": "Tam yönetim izinleri", "is_assignable": True},
            {"slug": "staff", "name": "Danışman", "description": "Operasyonel müşteri/randevu işleri", "is_assignable": True},
            {"slug": "viewer", "name": "İzleyici", "description": "Salt okunur erişim", "is_assignable": True},
        ],
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default="owner",
    )
    op.create_foreign_key(
        "fk_users_roles_role",
        source_table="users",
        referent_table="roles",
        local_cols=["role"],
        remote_cols=["slug"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_roles_role", "users", type_="foreignkey")
    op.drop_table("roles")
