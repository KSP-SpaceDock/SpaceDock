from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import _cfg

engine = create_engine(_cfg('connection-string'))
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db.query_property()


def init_db():
    # noinspection PyUnresolvedReferences
    from . import objects
    Base.metadata.create_all(bind=engine)
