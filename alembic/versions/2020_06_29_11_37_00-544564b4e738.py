"""Add announcement to blog

Revision ID: 544564b4e738
Revises: 85be165bc5dc
Create Date: 2020-06-29 11:37:00

"""

# revision identifiers, used by Alembic.
revision = '544564b4e738'
down_revision = '85be165bc5dc'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('blog', sa.Column('announcement', sa.Boolean(), nullable=True, default=False))
    op.create_index(op.f('ix_blog_announcement'), 'blog', ['announcement'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_announcement'), table_name='blog')
    op.drop_column('blog', 'announcement')
