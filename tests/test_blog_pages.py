"""Tests for blog blueprint pages."""
import pytest
from SpaceDock.objects import BlogPost
from SpaceDock.database import db


def test_blog_index(client):
    """Test blog index page."""
    response = client.get("/blog")
    assert response.status_code == 200


def test_blog_post_not_found(client):
    """Test viewing non-existent blog post."""
    response = client.get("/blog/99999")
    assert response.status_code == 404