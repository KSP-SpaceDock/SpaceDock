"""Index DownloadEvent columns

Revision ID: c0e44e063159
Revises: 73c9d707134b
Create Date: 2021-06-09 19:00:00

"""

# revision identifiers, used by Alembic.
revision = 'c0e44e063159'
down_revision = '73c9d707134b'

from datetime import datetime
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_index(op.f('ix_downloadevent_mod_id_created'), 'downloadevent', ['mod_id', 'created'], unique=False)
    op.create_index(op.f('ix_downloadevent_version_id_created'), 'downloadevent', ['version_id', 'created'], unique=False)
    op.drop_constraint('downloadevent_mod_id_fkey', 'downloadevent', type_='foreignkey')
    op.drop_constraint('downloadevent_version_id_fkey', 'downloadevent', type_='foreignkey')
    op.create_foreign_key('downloadevent_mod_id_fkey', 'downloadevent', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('downloadevent_version_id_fkey', 'downloadevent', 'modversion', ['version_id'], ['id'], ondelete='CASCADE')
    op.add_column('modversion', sa.Column('download_size', sa.BigInteger()))


def downgrade() -> None:
    op.drop_index(op.f('ix_downloadevent_mod_id_created'), table_name='downloadevent')
    op.drop_index(op.f('ix_downloadevent_version_id_created'), table_name='downloadevent')
    op.drop_constraint('downloadevent_mod_id_fkey', 'downloadevent', type_='foreignkey')
    op.drop_constraint('downloadevent_version_id_fkey', 'downloadevent', type_='foreignkey')
    op.create_foreign_key('downloadevent_version_id_fkey', 'downloadevent', 'modversion', ['version_id'], ['id'])
    op.create_foreign_key('downloadevent_mod_id_fkey', 'downloadevent', 'mod', ['mod_id'], ['id'])
    op.drop_column('modversion', 'download_size')
