"""Tests for SpaceDock/kerbdown.py."""
import pytest
from SpaceDock.kerbdown import KerbDown
from markdown import Markdown


def test_basic_markdown():
    """Test basic KerbDown markdown parsing."""
    md = Markdown(extensions=[KerbDown()])
    result = md.convert("# Hello\n\nThis is bold **text**.")
    assert "<h1>" in result
    assert "<strong>" in result


def test_embed_youtube_url():
    """Test YouTube embed via URL."""
    md = Markdown(extensions=[KerbDown()])
    result = md.convert('[[https://www.youtube.com/watch?v=dQw4w9WgXcQ]]')
    assert "iframe" in result


def test_embed_youtube_short():
    """Test YouTube embed via short URL."""
    md = Markdown(extensions=[KerbDown()])
    result = md.convert('[[https://youtu.be/dQw4w9WgXcQ]]')
    assert "iframe" in result


@pytest.mark.skip(reason="requires app context for url_for")
def test_at_username():
    """Test @username mention."""
    pass