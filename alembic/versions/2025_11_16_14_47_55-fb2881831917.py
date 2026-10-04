"""Add json_object to builds_url_format enum

Revision ID: fb2881831917
Revises: f5a5d29ec765
Create Date: 2025-11-16 20:47:58.636952

"""

# revision identifiers, used by Alembic.
revision = 'fb2881831917'
down_revision = 'f5a5d29ec765'

from alembic import op

def upgrade() -> None:
    op.execute("ALTER TYPE builds_url_format ADD VALUE IF NOT EXISTS 'json_object'")
    pass

def downgrade() -> None:
    # Can't remove enum values
    pass
