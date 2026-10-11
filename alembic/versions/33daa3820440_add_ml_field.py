"""add ML field

Revision ID: 33daa3820440
Revises: fb2881831917
Create Date: 2026-10-04 10:54:36.646387

"""

# revision identifiers, used by Alembic.
revision = '33daa3820440'
down_revision = 'fb2881831917'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column(
        'mod',
        sa.Column('ml', sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('mod', 'ml')
