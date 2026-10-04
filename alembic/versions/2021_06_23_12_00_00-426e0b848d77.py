"""Add BlogPost.members_only

Revision ID: 426e0b848d77
Revises: c0e44e063159
Create Date: 2021-06-23 12:00:00

"""

# revision identifiers, used by Alembic.
revision = '426e0b848d77'
down_revision = 'c0e44e063159'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # First create nullable column
    op.add_column('blog', sa.Column('members_only', sa.Boolean(), nullable=True, default=False))
    # Set existing rows to False, using raw SQL for simplicity
    op.execute("UPDATE blog SET members_only = false")
    # Set NULL announcement rows to false as well
    op.execute("UPDATE blog SET announcement = false WHERE announcement is NULL")
    # Make columns non-nullable
    op.alter_column('blog', 'members_only', nullable=False)
    op.alter_column('blog', 'announcement', nullable=False)
    op.create_index(op.f('ix_blog_members_only'), 'blog', ['members_only'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_members_only'), table_name='blog')
    op.drop_column('blog', 'members_only')
    op.alter_column('blog', 'announcement', nullable=True)
