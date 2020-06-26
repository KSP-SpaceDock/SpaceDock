"""Index ModList.created

Revision ID: 1aa078e0fb7e
Revises: 544564b4e738
Create Date: 2020-06-26 01:24:00

"""

# revision identifiers, used by Alembic.
revision = '1aa078e0fb7e'
down_revision = '544564b4e738'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_index(op.f('ix_modlist_created'), 'modlist', ['created'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_modlist_created'), table_name='modlist')
