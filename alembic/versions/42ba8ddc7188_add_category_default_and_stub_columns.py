"""add category default and stub columns

Revision ID: 42ba8ddc7188
Revises: 9eb6f3fea778
Create Date: 2026-10-16 12:10:50.191626

"""

# revision identifiers, used by Alembic.
revision = '42ba8ddc7188'
down_revision = '9eb6f3fea778'

from alembic import op
import sqlalchemy as sa


# Lightweight table definitions so we don't depend on the ORM models.
# SQLAlchemy takes care of quoting the reserved word "default".
game_mod_category = sa.table(
    'game_mod_category',
    sa.column('category_id', sa.Integer),
    sa.column('default', sa.Boolean),
)

mod_category = sa.table(
    'mod_category',
    sa.column('name', sa.String),
    sa.column('stub', sa.String),
)


def upgrade() -> None:
    # game_mod_category.default: boolean, defaults to false
    op.add_column(
        'game_mod_category',
        sa.Column('default', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    # Existing entries with category_id 1 become the default
    op.execute(
        game_mod_category.update()
        .where(game_mod_category.c.category_id == 1)
        .values({'default': True})
    )

    # mod_category.stub: varchar(255), filled with lower-cased name
    op.add_column('mod_category', sa.Column('stub', sa.String(255), nullable=True))
    op.execute(
        mod_category.update().values(stub=sa.func.lower(mod_category.c.name))
    )


def downgrade() -> None:
    op.drop_column('mod_category', 'stub')
    op.drop_column('game_mod_category', 'default')