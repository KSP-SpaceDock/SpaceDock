"""Add Game version to mod table

Revision ID: 3a3487af1b8
Revises: 46d0c3d3104
Create Date: 2014-06-06 01:06:46.794763

"""

# revision identifiers, used by Alembic.
revision = '3a3487af1b8'
down_revision = '46d0c3d3104'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mod', sa.Column('ksp_version', sa.String(length=16), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mod', 'ksp_version')
    ### end Alembic commands ###
