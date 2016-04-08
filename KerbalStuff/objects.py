from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text,Float
from sqlalchemy.orm import relationship, backref
from .database import Base
from KerbalStuff.config import _cfg
import KerbalStuff.thumbnail as thumbnail
import os.path

from datetime import datetime
import bcrypt

mod_followers = Table('mod_followers', Base.metadata,
    Column('mod_id', Integer, ForeignKey('mod.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
)

class Featured(Base):
    __tablename__ = 'featured'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', backref=backref('mod', order_by=id))
    created = Column(DateTime)

    def __init__(self):
        self.created = datetime.now()


    def __repr__(self):
        return '<Featured %r>' % self.id

class BlogPost(Base):
    __tablename__ = 'blog'
    id = Column(Integer, primary_key = True)
    title = Column(Unicode(1024))
    text = Column(Unicode(65535))
    created = Column(DateTime)

    def __init__(self):
        self.created = datetime.now()

    def __repr__(self):
        return '<Blog Post %r>' % self.id

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String(128), nullable = False, index = True)
    email = Column(String(256), nullable = False, index = True)
    public = Column(Boolean())
    admin = Column(Boolean())
    password = Column(String)
    description = Column(Unicode(10000))
    created = Column(DateTime)
    forumUsername = Column(String(128))
    forumId = Column(Integer)
    ircNick = Column(String(128))
    twitterUsername = Column(String(128))
    redditUsername = Column(String(128))
    location = Column(String(128))
    confirmation = Column(String(128))
    passwordReset = Column(String(128))
    passwordResetExpiry = Column(DateTime)
    backgroundMedia = Column(String(512))
    bgOffsetX = Column(Integer)
    bgOffsetY = Column(Integer)
    mods = relationship('Mod', order_by='Mod.created')
    packs = relationship('ModList', order_by='ModList.created')
    following = relationship('Mod', secondary=mod_followers, backref='user.id')
    dark_theme = Column(Boolean())

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.public = False
        self.admin = False
        self.created = datetime.now()
        self.twitterUsername = ''
        self.forumUsername = ''
        self.ircNick = ''
        self.description = ''
        self.backgroundMedia = ''
        self.bgOffsetX = 0
        self.bgOffsetY = 0
        self.dark_theme = False
    def __repr__(self):
        return '<User %r>' % self.username

    # Flask.Login stuff
    # We don't use most of these features
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username


class UserAuth(Base):
    __tablename__ = 'user_auth'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    provider = Column(String(32))  # 'github' or 'google', etc.
    remote_user = Column(String(128), index=True)  # Usually the username on the other side
    created = Column(DateTime)
    # We can keep a token here, to allow interacting with the provider's API
    # on behalf of the user.

    def __init__(self, user_id, remote_user, provider):
        self.user_id = user_id
        self.provider = provider
        self.remote_user = remote_user
        self.created = datetime.now()

    def __repr__(self):
        return '<UserAuth %r, User %r>' % (self.provider, self.user_id)

class Publisher(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key = True)
    name = Column(Unicode(1024))
    short_description = Column(Unicode(1000))
    description = Column(Unicode(100000))
    created = Column(DateTime)
    updated = Column(DateTime)
    background = Column(String(512))
    bgOffsetX = Column(Integer)
    bgOffsetY = Column(Integer)
    link = Column(Unicode(1024))
    games = relationship('Game', back_populates='publisher')

    def __init__(self,name):
        self.created = datetime.now()
        self.name = name

    def __repr__(self):
        return '<Publisher %r %r>' % (self.id, self.name)

class Game(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key = True)
    name = Column(Unicode(1024))
    active = Column(Boolean())
    fileformats = Column(Unicode(1024))
    altname = Column(Unicode(1024))
    rating = Column(Float())
    releasedate = Column(DateTime)
    short = Column(Unicode(1024))
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    publisher = relationship('Publisher', back_populates='games')
    description = Column(Unicode(100000))
    short_description = Column(Unicode(1000))
    created = Column(DateTime)
    updated = Column(DateTime)
    background = Column(String(512))
    bgOffsetX = Column(Integer)
    bgOffsetY = Column(Integer)
    link = Column(Unicode(1024))
    mods = relationship('Mod', back_populates='game')
    modlists = relationship('ModList', back_populates='game')
    version = relationship('GameVersion', back_populates='game')

    def __init__(self,name,publisher_id,short):
        self.created = datetime.now()
        self.name = name
        self.publisher_id = publisher_id
        self.short = short

    def __repr__(self):
        return '<Game %r %r>' % (self.id, self.name)

class Mod(Base):
    __tablename__ = 'mod'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('mod', order_by=id))
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship('Game', back_populates='mods')
    shared_authors = relationship('SharedAuthor')
    name = Column(String(100), index = True)
    description = Column(Unicode(100000))
    short_description = Column(Unicode(1000))
    approved = Column(Boolean())
    published = Column(Boolean())
    donation_link = Column(String(512))
    external_link = Column(String(512))
    license = Column(String(128))
    votes = Column(Integer())
    created = Column(DateTime)
    updated = Column(DateTime)
    background = Column(String(512))
    bgOffsetX = Column(Integer)
    bgOffsetY = Column(Integer)
    medias = relationship('Media')
    default_version_id = Column(Integer)
    versions = relationship('ModVersion', order_by="desc(ModVersion.sort_index)")
    downloads = relationship('DownloadEvent', order_by="desc(DownloadEvent.created)")
    follow_events = relationship('FollowEvent', order_by="desc(FollowEvent.created)")
    referrals = relationship('ReferralEvent', order_by="desc(ReferralEvent.created)")
    source_link = Column(String(256))
    follower_count = Column(Integer, nullable=False, server_default=text('0'))
    download_count = Column(Integer, nullable=False, server_default=text('0'))
    followers = relationship('User', viewonly=True, secondary=mod_followers, backref='mod.id')
    ckan = Column(Boolean)
    
    def background_thumb(self):
        if (_cfg('thumbnail_size') == ''):
            return self.background
        thumbnailSizesStr = _cfg('thumbnail_size').split('x')
        thumbnailSize = (int(thumbnailSizesStr[0]), int(thumbnailSizesStr[1]))
        split = os.path.split(self.background)
        thumbPath = os.path.join(split[0], 'thumb_' + split[1])
        fullThumbPath = os.path.join(os.path.join(_cfg('storage'), thumbPath.replace('/content/', '')))
        fullImagePath = os.path.join(_cfg('storage'), self.background.replace('/content/', ''))
        if not os.path.exists(fullThumbPath):
            thumbnail.create(fullImagePath, fullThumbPath, thumbnailSize)
        return thumbPath

    def default_version(self):
        versions = [v for v in self.versions if v.id == self.default_version_id]
        if len(versions) == 0:
            return None
        return versions[0]

    def serialize(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'name': self.name,
            'description': self.description,
            'short_Description': self.short_description,
            'published': self.published,
            'license': self.license,
            'votes': self.votes,
            'created': self.created,
            'updated': self.updated,
            'background': self.background,
            #'thumbnail': self.background_thumb(),
            'default_version_id': self.default_version_id,
            'default_version': self.default_version().ksp_version,
            'download_count': self.download_count,
            'follower_count': self.follower_count,
            'ckan': self.ckan
        }

    def __init__(self):
        self.created = datetime.now()
        self.updated = datetime.now()
        self.approved = False
        self.published = False
        self.votes = 0
        self.follower_count = 0
        self.download_count = 0

    def __repr__(self):
        return '<Mod %r %r>' % (self.id, self.name)

class ModList(Base):
    __tablename__ = 'modlist'
    id = Column(Integer, primary_key = True)
    user = relationship('User', backref=backref('modlist', order_by=id))
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime)
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship('Game', back_populates='modlists')
    background = Column(String(32))
    bgOffsetY = Column(Integer)
    description = Column(Unicode(100000))
    short_description = Column(Unicode(1000))
    name = Column(Unicode(1024))
    mods = relationship('ModListItem', order_by="asc(ModListItem.sort_index)")

    def __init__(self):
        self.created = datetime.now()

    def __repr__(self):
        return '<ModList %r %r>' % (self.id, self.name)

class ModListItem(Base):
    __tablename__ = 'modlistitem'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('modlistitem'))
    mod_list_id = Column(Integer, ForeignKey('modlist.id'))
    mod_list = relationship('ModList', viewonly=True, backref=backref('modlistitem'))
    sort_index = Column(Integer)

    def __init__(self):
        self.sort_index = 0

    def __repr__(self):
        return '<ModListItem %r %r>' % (self.mod_id, self.mod_list_id)

class SharedAuthor(Base):
    __tablename__ = 'sharedauthor'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('sharedauthor'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('sharedauthor', order_by=id))
    accepted = Column(Boolean)

    def __init__(self):
        self.accepted = False

    def __repr__(self):
        return '<SharedAuthor %r>' % self.user_id

class DownloadEvent(Base):
    __tablename__ = 'downloadevent'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('downloadevent', order_by="desc(DownloadEvent.created)"))
    version_id = Column(Integer, ForeignKey('modversion.id'))
    version = relationship('ModVersion', backref=backref('downloadevent', order_by="desc(DownloadEvent.created)"))
    downloads = Column(Integer)
    created = Column(DateTime)

    def __init__(self):
        self.downloads = 0
        self.created = datetime.now()

    def __repr__(self):
        return '<Download Event %r>' % self.id

class FollowEvent(Base):
    __tablename__ = 'followevent'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('followevent', order_by="desc(FollowEvent.created)"))
    events = Column(Integer)
    delta = Column(Integer)
    created = Column(DateTime)

    def __init__(self):
        self.delta = 0
        self.created = datetime.now()

    def __repr__(self):
        return '<Download Event %r>' % self.id

class ReferralEvent(Base):
    __tablename__ = 'referralevent'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('referralevent', order_by="desc(ReferralEvent.created)"))
    host = Column(String)
    events = Column(Integer)
    created = Column(DateTime)

    def __init__(self):
        self.events = 0
        self.created = datetime.now()

    def __repr__(self):
        return '<Download Event %r>' % self.id

class ModVersion(Base):
    __tablename__ = 'modversion'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('modversion', order_by="desc(ModVersion.created)"))
    friendly_version = Column(String(64))
    gameversion_id = Column(Integer, ForeignKey('gameversion.id'))
    gameversion = relationship('GameVersion', viewonly=True, backref=backref('modversion', order_by=id))
    created = Column(DateTime)
    download_path = Column(String(512))
    changelog = Column(Unicode(10000))
    sort_index = Column(Integer)

    def __init__(self, friendly_version, gameversion_id, download_path):
        self.friendly_version = friendly_version
        self.gameversion_id = gameversion_id
        self.download_path = download_path
        self.created = datetime.now()
        self.sort_index = 0

    def __repr__(self):
        return '<Mod Version %r>' % self.id

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key = True)
    mod_id = Column(Integer, ForeignKey('mod.id'))
    mod = relationship('Mod', viewonly=True, backref=backref('media', order_by=id))
    hash = Column(String(12))
    type = Column(String(32))
    data = Column(String(512))

    def __init__(self, hash, type, data):
        self.hash = hash
        self.type = type
        self.data = data

    def __repr__(self):
        return '<Media %r>' % self.hash

class GameVersion(Base):
    __tablename__ = 'gameversion'
    id = Column(Integer, primary_key = True)
    friendly_version = Column(String(128))
    game_id = Column(Integer, ForeignKey('game.id'))
    game = relationship('Game', back_populates='version')


    def __init__(self, friendly_version, game_id):
        self.friendly_version = friendly_version
        self.game_id = game_id

    def __repr__(self):
        return '<Game Version %r>' % self.friendly_version
