from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import _cfg

engine = create_engine(_cfg('connection-string'))
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db.query_property()


def create_database() -> bool:
    """Create the database of the service using the preconfigured backend."""
    from sqlalchemy_utils import database_exists, create_database as sqla_create_db
    if not database_exists(engine.url):
        sqla_create_db(engine.url)
        return True
    return False


def drop_database() -> None:
    """Drop the database of the service from the preconfigured backend."""
    from sqlalchemy_utils import database_exists, drop_database as sqla_drop_db
    if database_exists(engine.url):
        sqla_drop_db(engine.url)


def create_tables() -> None:
    """
    Create database tables required for the service.
    For this to work the database already created.
    """
    # noinspection PyUnresolvedReferences
    from . import objects
    Base.metadata.create_all(engine)


def drop_tables() -> None:
    """
    Drops the database tables used by the service.
    For this to work the database already created.
    """
    # noinspection PyUnresolvedReferences
    from . import objects
    Base.metadata.drop_all(engine)
