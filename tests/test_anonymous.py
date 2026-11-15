"""Tests for anonymous blueprint pages."""
import pytest


def test_index_page(client):
    """Test main index page."""
    response = client.get("/")
    assert response.status_code == 200


def test_about_page(client):
    """Test about page."""
    response = client.get("/about")
    assert response.status_code == 200


def test_privacy_page(client):
    """Test privacy page."""
    response = client.get("/privacy")
    assert response.status_code == 200


def test_markdown_page(client):
    """Test markdown info page."""
    response = client.get("/markdown")
    assert response.status_code == 200


def test_search_page(client):
    """Test search page."""
    response = client.get("/search")
    assert response.status_code == 200


def test_search_with_query(client):
    """Test search with query."""
    response = client.get("/search?query=test")
    assert response.status_code == 200