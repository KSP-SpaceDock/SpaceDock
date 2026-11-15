"""Tests for lists blueprint pages."""
import pytest
from SpaceDock.objects import ModList
from SpaceDock.database import db


def test_packs_index(client):
    """Test packs index page."""
    response = client.get("/packs")
    assert response.status_code == 200


def test_create_pack_form(client):
    """Test pack creation form."""
    response = client.get("/create/pack")
    assert response.status_code == 200