"""Add steamUsername, discordUsername, and youtubeUsername columns to user

Revision ID: ba0c9afb6cb0
Revises: f7d352d49c2b
Create Date: 2023-04-09 00:02:54.923875

"""

# revision identifiers, used by Alembic.
revision = 'ba0c9afb6cb0'
down_revision = 'f7d352d49c2b'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('user', sa.Column('steamUsername', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('discordUsername', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('youtubeUsername', sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'youtubeUsername')
    op.drop_column('user', 'discordUsername')
    op.drop_column('user', 'steamUsername')
