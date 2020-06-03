"""Add Notifications table

Revision ID: f7d352d49c2b
Revises: 7eec82634342
Create Date: 2023-03-20 16:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = 'f7d352d49c2b'
down_revision = '7eec82634342'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from KerbalStuff.config import _cfg

Base = declarative_base()


class Game(Base):  # type: ignore
    __tablename__ = 'game'
    id = sa.Column(sa.Integer, primary_key=True)


class Mod(Base):  # type: ignore
    __tablename__ = 'mod'
    id = sa.Column(sa.Integer, primary_key=True)
    game_id = sa.Column(sa.Integer, sa.ForeignKey('game.id'))
    game = relationship('Game', backref='mods')
    ckan = sa.Column(sa.Boolean)


class Notification(Base):  # type: ignore
    __tablename__ = 'notification'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(1024), nullable=False)
    game_id = sa.Column(sa.Integer, sa.ForeignKey('game.id', ondelete='CASCADE'), nullable=False, index=True)
    game = relationship('Game', backref=backref('notifications', passive_deletes='all'), passive_deletes='all', foreign_keys=game_id)
    builds_url = sa.Column(sa.Unicode(1024))
    builds_url_format = sa.Column(sa.Enum('plain_current', 'json_nested_dict_values', 'json_list', name='builds_url_format'))
    builds_url_argument = sa.Column(sa.Unicode(32))
    add_url = sa.Column(sa.Unicode(1024))
    change_url = sa.Column(sa.Unicode(1024))

    def __repr__(self) -> str:
        return f'<Notification {self.id} {self.name}>'


class EnabledNotification(Base):  # type: ignore
    __tablename__ = 'enablednotification'
    id = sa.Column(sa.Integer, primary_key=True)
    notification_id = sa.Column(sa.Integer, sa.ForeignKey('notification.id', ondelete='CASCADE'), nullable=False)
    notification = relationship('Notification', backref=backref('enabled_mods', passive_deletes='all'), passive_deletes='all', foreign_keys=notification_id)
    mod_id = sa.Column(sa.Integer, sa.ForeignKey('mod.id', ondelete='CASCADE'), nullable=False, index=True)
    mod = relationship('Mod', backref=backref('enabled_notifications', passive_deletes='all'), passive_deletes='all', foreign_keys=mod_id)

    def __repr__(self) -> str:
        return f'<EnabledNotification {self.id} {self.notification_id} {self.mod_id}>'


def upgrade() -> None:
    op.create_table('notification',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('name', sa.VARCHAR(1024), nullable=False),
                    sa.Column('game_id', sa.INTEGER, sa.ForeignKey('game.id', ondelete='CASCADE'), nullable=False, index=True),
                    sa.Column('builds_url', sa.VARCHAR(1024)),
                    sa.Column('builds_url_format', sa.Enum('plain_current', 'json_nested_dict_values', 'json_list', name='builds_url_format')),
                    sa.Column('builds_url_argument', sa.VARCHAR(32)),
                    sa.Column('add_url', sa.VARCHAR(1024)),
                    sa.Column('change_url', sa.VARCHAR(1024)))
    op.create_table('enablednotification',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('notification_id', sa.INTEGER, sa.ForeignKey('notification.id', ondelete='CASCADE'), nullable=False),
                    sa.Column('mod_id', sa.INTEGER, sa.ForeignKey('mod.id', ondelete='CASCADE'), nullable=False, index=True))

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    ksp_game_id = _cfg('ksp-game-id')
    if ksp_game_id:
        notif = Notification(name='CKAN',
                             game_id=ksp_game_id,
                             builds_url='https://github.com/KSP-CKAN/CKAN-meta/raw/master/builds.json',
                             builds_url_format='json_nested_dict_values',
                             builds_url_argument='builds',
                             add_url='https://netkan.ksp-ckan.space/sd/add',
                             change_url='https://netkan.ksp-ckan.space/sd/inflate')
        session.add(notif)
        for mod in session.query(Mod).filter(Mod.ckan == True, Mod.game_id == ksp_game_id).all():
            enab_notif = EnabledNotification(notification_id=notif.id,
                                             mod_id=mod.id)
            session.add(enab_notif)

    ksp2_game_id = _cfg('ksp2-game-id')
    if ksp2_game_id:
        notif = Notification(name='CKAN',
                             game_id=ksp2_game_id,
                             builds_url='https://github.com/KSP-CKAN/KSP2-CKAN-meta/raw/main/builds.json',
                             builds_url_format='json_list',
                             add_url='https://netkan.ksp-ckan.space/sd/add/ksp2',
                             change_url='https://netkan.ksp-ckan.space/sd/inflate/ksp2')
        session.add(notif)
        for mod in session.query(Mod).filter(Mod.ckan == True, Mod.game_id == ksp2_game_id).all():
            session.add(EnabledNotification(notification_id=notif.id,
                                            mod_id=mod.id))

    session.commit()
    op.drop_column('mod', 'ckan')


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    op.add_column('mod', sa.Column('ckan', sa.Boolean))
    for enab_notif in session.query(EnabledNotification).all():
        enab_notif.mod.ckan = True

    session.commit()
    op.drop_table('enablednotification')
    op.drop_table('notification')
    op.execute('DROP TYPE builds_url_format')
