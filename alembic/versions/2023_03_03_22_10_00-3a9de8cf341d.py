"""Add BlogPost.draft

Revision ID: 3a9de8cf341d
Revises: 76ba7330ce15
Create Date: 2023-03-03 22:10:00.000000

"""

# revision identifiers, used by Alembic.
revision = '3a9de8cf341d'
down_revision = '76ba7330ce15'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('blog', sa.Column('draft', sa.Boolean(), nullable=True, default=False))
    op.create_index(op.f('ix_blog_draft'), 'blog', ['draft'], unique=False)
    op.execute("UPDATE blog SET draft = false")
    op.alter_column('blog', 'draft', nullable=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_draft'), table_name='blog')
    op.drop_column('blog', 'draft')
