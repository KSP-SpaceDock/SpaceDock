"""Add categories to packs

Revision ID: 67f37732c112
Revises: 42ba8ddc7188
Create Date: 2026-10-19 06:21:18.079299
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = '67f37732c112'
down_revision = '42ba8ddc7188'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'modlist',
        sa.Column(
            'category',
            sa.Integer(),
            nullable=False,
            server_default='1',
        ),
    )

    op.create_foreign_key(
        'fk_modlist_category_mod_category',
        'modlist',
        'mod_category',
        ['category'],
        ['id'],
        ondelete='RESTRICT',
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_modlist_category_mod_category',
        'modlist',
        type_='foreignkey',
    )
    op.drop_column('modlist', 'category')