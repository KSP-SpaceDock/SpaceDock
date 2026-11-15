"""Tests for SpaceDock/antivirus.py."""
import pytest
from SpaceDock.antivirus import file_contains_malware, quarantine_malware


def test_file_contains_malware_missing_daemon():
    """Test file scan without ClamAV daemon (should not crash)."""
    result = file_contains_malware("/tmp/test_file.txt")
    assert isinstance(result, bool)


def test_quarantine_malware():
    """Test quarantining malware."""
    import tempfile, os
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    quarantine_malware(f.name)
    assert not os.path.exists(f.name)