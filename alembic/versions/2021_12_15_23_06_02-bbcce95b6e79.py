"""Create mod_similarity table

Revision ID: bbcce95b6e79
Revises: 3fb8a6e2e0a5
Create Date: 2021-12-16 05:06:06.312797

"""

# revision identifiers, used by Alembic.
revision = 'bbcce95b6e79'
down_revision = '3fb8a6e2e0a5'

from alembic import op
from alembic.op import create_table, drop_table
import sqlalchemy as sa

from KerbalStuff.celery import update_mod_similarities

Base = sa.ext.declarative.declarative_base()

class Mod(Base):  # type: ignore
    __tablename__ = 'mod'
    id = sa.Column(sa.Integer, primary_key=True)
    published = sa.Column(sa.Boolean, default=False)


def upgrade() -> None:
    create_table('mod_similarity',
                 sa.Column('main_mod_id', sa.Integer(), nullable=False),
                 sa.Column('other_mod_id', sa.Integer(), nullable=False),
                 sa.Column('similarity', sa.Float(precision=5), nullable=False),
                 sa.ForeignKeyConstraint(['main_mod_id'], ['mod.id'], ondelete='CASCADE'),
                 sa.ForeignKeyConstraint(['other_mod_id'], ['mod.id'], ondelete='CASCADE'),
                 sa.PrimaryKeyConstraint('main_mod_id', 'other_mod_id', name='pk_mods'))
    op.create_index('ix_mod_similarity_main_mod_similarity',
                    'mod_similarity', ['main_mod_id', sa.text('similarity DESC')], unique=False)

    # Ask Celery to build the similarity rows for existing published mods
    update_mod_similarities.delay([mod_id for mod_id, in
                                   sa.orm.Session(bind=op.get_bind())
                                         .query(Mod)
                                         .filter(Mod.published)
                                         .with_entities(Mod.id)])

def downgrade() -> None:
    op.drop_index('ix_mod_similarity_main_mod_similarity', table_name='mod_similarity')
    drop_table('mod_similarity')
