"""Add kerbalxUsername and githubUsername columns to user

Revision ID: 3fb8a6e2e0a5
Revises: 1cbfc1acd83d
Create Date: 2021-07-30 22:19:05.680749

"""

# revision identifiers, used by Alembic.
revision = '3fb8a6e2e0a5'
down_revision = '1cbfc1acd83d'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('user', sa.Column('kerbalxUsername', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('githubUsername', sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'githubUsername')
    op.drop_column('user', 'kerbalxUsername')
