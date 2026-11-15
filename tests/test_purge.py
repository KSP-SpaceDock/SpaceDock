"""Tests for SpaceDock/purge.py."""
import pytest
from SpaceDock.purge import purge_download


def test_purge_download():
    """Test purging download path."""
    purge_download("test/path/file.zip")


def test_purge_download_empty():
    """Test purging with empty path."""
    purge_download("")