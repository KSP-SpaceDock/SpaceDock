"""Added foreign key constraint to mod.default_version_id

Revision ID: 77f76102f99c
Revises: 6ffd5dd5efab
Create Date: 2019-08-28 22:09:12.339019

"""

# revision identifiers, used by Alembic.
revision = '77f76102f99c'
down_revision = '6ffd5dd5efab'

from alembic import op


def upgrade() -> None:
    op.create_foreign_key('mod_default_ver_modversion_id_fk',
                          'mod', 'modversion',
                          ['default_version_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('mod_default_ver_modversion_id_fk', 'mod', type_='foreignkey')
