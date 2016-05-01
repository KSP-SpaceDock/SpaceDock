"""switch ksp_version to game_version

Revision ID: 6ffd5dd5efab
Revises: 4e0500347ce7
Create Date: 2016-04-08 22:58:14.178434

"""

# revision identifiers, used by Alembic.
revision = '6ffd5dd5efab'
down_revision = '4e0500347ce7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('modversion', sa.Column('gameversion_id', sa.Integer(), nullable=True))
    op.create_foreign_key('modversion_gameversion_id_fkey', 'modversion', 'gameversion', ['gameversion_id'], ['id'])
    op.execute('update modversion set gameversion_id=(select gameversion.id from gameversion where modversion.ksp_version = gameversion.friendly_version and gameversion.game_id = (SELECT mod.game_id from mod where mod.id=modversion.mod_id));')
    op.drop_column('modversion', 'ksp_version')


def downgrade():
    op.add_column('modversion', sa.Column('ksp_version', sa.String(64), nullable=True))
    op.execute('update modversion set ksp_version=(select gameversion.friendly_version from gameversion where modversion.gameversion_id = gameversion.id);')
    op.drop_constraint('modversion_gameversion_id_fkey', 'modversion', type_='foreignkey')
    op.drop_column('modversion', 'gameversion_id')
