from typing import Generator

import pytest
from flask.testing import FlaskClient
from flask import Response
from flask_api import status

from .fake_db import dummy
from KerbalStuff.app import app


# FlaskClient requires a type parameter in mypy, but errors out with one at runtime
@pytest.fixture
def client() -> Generator['FlaskClient[Response]', None, None]:
    with app.test_client() as client:
        yield client


def test_version(client: 'FlaskClient[Response]') -> None:
    resp = client.get('/version')
    assert resp.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert resp.data.startswith(b'commit'), 'Response should start with "commit"'
    assert b'\nAuthor: ' in resp.data, 'Response should return a Author header'
    assert b'\nDate: ' in resp.data, 'Response should return a Date header'
