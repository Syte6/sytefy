"""${message}"""

revision = "${up_revision}"
down_revision = ${down_revision | repr}
branch_labels = ${branch_labels | repr}
depends_on = ${depends_on | repr}

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
${upgrades or '    pass'}


def downgrade() -> None:
${downgrades or '    pass'}
