"""Add ModVersion.changelog_html

Revision ID: 1b3f98f3620d
Revises: 3fb8a6e2e0a5
Create Date: 2021-10-28 01:24:57.435381

"""

# revision identifiers, used by Alembic.
revision = '1b3f98f3620d'
down_revision = '3fb8a6e2e0a5'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('modversion', sa.Column('changelog_html', sa.Unicode(length=20000), nullable=True))


def downgrade() -> None:
    op.drop_column('modversion', 'changelog_html')
