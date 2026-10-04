"""Create Game.thumbnail

Revision ID: b9e4c97b74c1
Revises: 3a9de8cf341d
Create Date: 2023-03-14 18:49:24.632850

"""

# revision identifiers, used by Alembic.
revision = 'b9e4c97b74c1'
down_revision = '3a9de8cf341d'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('game', sa.Column('thumbnail', sa.VARCHAR(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('game', 'thumbnail')
