from typing import Generator
import pytest
from flask.testing import FlaskClient
from flask import Response

from tests.fake_db import dummy
from KerbalStuff.app import app

# FlaskClient requires a type parameter in mypy, but errors out with one at runtime
@pytest.fixture
def client() -> Generator['FlaskClient[Response]', None, None]:
    with app.test_client() as client:
        yield client
