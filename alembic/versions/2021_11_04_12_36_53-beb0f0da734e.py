"""Create ModList.thumbnail

Revision ID: beb0f0da734e
Revises: 44040211d4e7
Create Date: 2021-11-04 17:36:56.561913

"""

# revision identifiers, used by Alembic.
revision = 'beb0f0da734e'
down_revision = '44040211d4e7'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.alter_column('modlist', 'background', type_=sa.String(length=512))
    op.add_column('modlist', sa.Column('thumbnail', sa.String(length=512), nullable=True))


def downgrade() -> None:
    # Shortening the ModList.background column breaks if we stored long strings in it and isn't needed for the old code to work
    op.drop_column('modlist', 'thumbnail')
