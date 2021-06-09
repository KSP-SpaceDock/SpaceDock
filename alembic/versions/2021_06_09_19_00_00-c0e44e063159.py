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


def upgrade() -> None:
    op.create_index(op.f('ix_downloadevent_mod_id_created'), 'downloadevent', ['mod_id', 'created'], unique=False)
    op.create_index(op.f('ix_downloadevent_version_id_created'), 'downloadevent', ['version_id', 'created'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_downloadevent_mod_id_created'), table_name='downloadevent')
    op.drop_index(op.f('ix_downloadevent_version_id_created'), table_name='downloadevent')
