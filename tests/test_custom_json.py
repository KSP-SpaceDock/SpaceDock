"""Tests for SpaceDock/custom_json.py."""
import json
from datetime import datetime, timezone
from SpaceDock.custom_json import CustomJSONEncoder


def test_datetime_serialization():
    """Test datetime serialization."""
    dt = datetime.now(timezone.utc)
    result = json.dumps(dt, cls=CustomJSONEncoder)
    assert isinstance(result, str)


def test_set_serialization():
    """Test set serialization."""
    data = {"tags": {"python", "flask"}}
    result = json.dumps(data, cls=CustomJSONEncoder)
    assert isinstance(result, str)