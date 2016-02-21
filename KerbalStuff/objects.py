from sqlalchemy import Column, Integer, String, Unicode, Boolean, DateTime, ForeignKey, Table, UnicodeText, Text, text
from sqlalchemy.orm import relationship, backref
from .database import Base

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
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
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


class Mod(Base):
    __tablename__ = 'mod'
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref=backref('mod', order_by=id))
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

    def default_version(self):
        versions = [v for v in self.versions if v.id == self.default_version_id]
        if len(versions) == 0:
            return None
        return versions[0]

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
    ksp_version = Column(String(64))
    created = Column(DateTime)
    download_path = Column(String(512))
    changelog = Column(Unicode(10000))
    sort_index = Column(Integer)

    def __init__(self, friendly_version, ksp_version, download_path):
        self.friendly_version = friendly_version
        self.ksp_version = ksp_version
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

    def __init__(self, friendly_version):
        self.friendly_version = friendly_version

    def __repr__(self):
        return '<Game Version %r>' % self.friendly_version
