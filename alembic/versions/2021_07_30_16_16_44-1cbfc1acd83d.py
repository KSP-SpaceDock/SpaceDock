"""Make most of modlistitem non-nullable

Revision ID: 1cbfc1acd83d
Revises: 833ba1ee8c72
Create Date: 2021-07-30 16:16:44

"""

# revision identifiers, used by Alembic.
revision = '1cbfc1acd83d'
down_revision = '833ba1ee8c72'

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Remove broken rows
    op.execute("DELETE FROM modlistitem WHERE mod_id is NULL OR mod_list_id is NULL OR sort_index is NULL")

    # Make most of the columns non-nullable
    op.alter_column('modlistitem', 'mod_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('modlistitem', 'mod_list_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('modlistitem', 'sort_index', existing_type=sa.INTEGER(), nullable=False)

    # Cascade deletion for the mod and mod list
    op.drop_constraint('modlistitem_mod_list_id_fkey', 'modlistitem', type_='foreignkey')
    op.drop_constraint('modlistitem_mod_id_fkey', 'modlistitem', type_='foreignkey')
    op.create_foreign_key('modlistitem_mod_list_id_fkey', 'modlistitem', 'modlist', ['mod_list_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('modlistitem_mod_id_fkey', 'modlistitem', 'mod', ['mod_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('modlistitem_mod_id_fkey', 'modlistitem', type_='foreignkey')
    op.drop_constraint('modlistitem_mod_list_id_fkey', 'modlistitem', type_='foreignkey')
    op.create_foreign_key('modlistitem_mod_id_fkey', 'modlistitem', 'mod', ['mod_id'], ['id'])
    op.create_foreign_key('modlistitem_mod_list_id_fkey', 'modlistitem', 'modlist', ['mod_list_id'], ['id'])
    op.alter_column('modlistitem', 'sort_index', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('modlistitem', 'mod_list_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('modlistitem', 'mod_id', existing_type=sa.INTEGER(), nullable=True)
