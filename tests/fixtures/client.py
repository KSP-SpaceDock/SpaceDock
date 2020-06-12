from typing import Generator
import pytest
from flask.testing import FlaskClient
from flask import Response

from tests.fake_db import dummy
from KerbalStuff.database import create_database, create_tables, drop_database, drop_tables
from KerbalStuff.app import app

# FlaskClient requires a type parameter in mypy, but errors out with one at runtime
@pytest.fixture
def client() -> Generator['FlaskClient[Response]', None, None]:
    # create_database has a meaningless return value, don't assert it
    create_database()
    create_tables()
    with app.test_client() as client:
        yield client
    drop_tables()
