"""Make DownloadEvent index descending order

Revision ID: 44040211d4e7
Revises: 1b3f98f3620d
Create Date: 2021-10-28 15:32:13.077268

"""

# revision identifiers, used by Alembic.
revision = '44040211d4e7'
down_revision = '1b3f98f3620d'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.drop_index(op.f('ix_downloadevent_mod_id_created'), table_name='downloadevent')
    op.drop_index(op.f('ix_downloadevent_version_id_created'), table_name='downloadevent')

    op.create_index(op.f('ix_downloadevent_mod_id_created'), 'downloadevent', ['mod_id', sa.text('created desc')], unique=False)
    op.create_index(op.f('ix_downloadevent_version_id_created'), 'downloadevent', ['version_id', sa.text('created desc')], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_downloadevent_mod_id_created'), table_name='downloadevent')
    op.drop_index(op.f('ix_downloadevent_version_id_created'), table_name='downloadevent')

    op.create_index(op.f('ix_downloadevent_mod_id_created'), 'downloadevent', ['mod_id', 'created'], unique=False)
    op.create_index(op.f('ix_downloadevent_version_id_created'), 'downloadevent', ['version_id', 'created'], unique=False)
