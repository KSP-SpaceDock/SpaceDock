"""Add featured.priority

Revision ID: f5a5d29ec765
Revises: ba0c9afb6cb0
Create Date: 2024-01-02 20:57:00.647417

"""

# revision identifiers, used by Alembic.
revision = 'f5a5d29ec765'
down_revision = 'ba0c9afb6cb0'

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

Base = sa.orm.declarative_base()

class Featured(Base):  # type: ignore
    __tablename__ = 'featured'
    id = sa.Column(sa.Integer, primary_key=True)
    mod_id = sa.Column(sa.Integer, sa.ForeignKey('mod.id', ondelete='CASCADE'))
    mod = relationship('Mod', backref=backref('featured', passive_deletes=True, order_by=id))
    created = sa.Column(sa.DateTime, default=datetime.now, index=True)
    priority = sa.Column(sa.Integer, nullable=False, index=True)


class Mod(Base):  # type: ignore
    __tablename__ = 'mod'
    id = sa.Column(sa.Integer, primary_key=True)
    game_id = sa.Column(sa.Integer, sa.ForeignKey('game.id', ondelete='CASCADE'))
    game = relationship('Game', backref=backref('mods', passive_deletes=True))


class Game(Base):  # type: ignore
    __tablename__ = 'game'
    id = sa.Column(sa.Integer, primary_key=True)


def upgrade() -> None:
    op.add_column('featured', sa.Column('priority', sa.Integer(), nullable=True))
    op.create_index('ix_featured_priority', 'featured', [sa.text('priority DESC')], unique=False)

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    prio = 0
    game_id = None
    for feature in session.query(Featured)\
                          .outerjoin(Mod)\
                          .order_by(Mod.game_id, Featured.created)\
                          .all():
        prio = prio + 1 if game_id == feature.mod.game_id else 0
        game_id = feature.mod.game_id
        feature.priority = prio
    session.commit()

    op.alter_column('featured', 'priority', nullable=False)


def downgrade() -> None:
    op.drop_index('ix_featured_priority', table_name='featured')
    op.drop_column('featured', 'priority')
