"""Add thumbnail column for mod table

Revision ID: 833ba1ee8c72
Revises: 17fbd4ff8193
Create Date: 2021-07-29 18:50:08.327728+00:00

"""

# revision identifiers, used by Alembic.
revision = '833ba1ee8c72'
down_revision = '17fbd4ff8193'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.execute("""UPDATE mod SET background = trim(LEADING '/content/' FROM background)
                  WHERE background IS NOT NULL AND background != '' """)
    op.execute("""UPDATE "user" SET "backgroundMedia" = trim(LEADING '/content/' FROM "backgroundMedia")
                  WHERE "backgroundMedia" IS NOT NULL AND "backgroundMedia" != '' """)

    op.add_column('mod', sa.Column('thumbnail', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('mod', 'thumbnail')
