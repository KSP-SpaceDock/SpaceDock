"""Index Mod.locked,Mod.updated

Revision ID: 76ba7330ce15
Revises: beb0f0da734e
Create Date: 2023-03-03 22:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = '76ba7330ce15'
down_revision = 'beb0f0da734e'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_index('ix_mod_locked_updated', 'mod', ['locked', sa.text('updated DESC')], unique=False)


def downgrade() -> None:
    op.drop_index('ix_mod_locked_updated', table_name='mod')
