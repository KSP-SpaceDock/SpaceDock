"""Tests for SpaceDock/thumbnail.py."""
import pytest
import os
from SpaceDock.thumbnail import create, thumb_path_from_background_path


def test_thumb_path_from_background_path():
    """Test thumbnail path calculation."""
    result = thumb_path_from_background_path("/path/to/background.jpg")
    assert result == "/path/to/thumb_background.jpg"
    
    # Function always returns jpg extension regardless of input
    result = thumb_path_from_background_path("/path/to/file.png")
    assert result == "/path/to/thumb_file.jpg"


def test_create_thumbnail():
    """Test thumbnail creation."""
    import tempfile
    
    # Create a test image
    from PIL import Image
    tmp_dir = tempfile.mkdtemp()
    background_path = os.path.join(tmp_dir, "test_bg.jpg")
    thumb_path = os.path.join(tmp_dir, "test_thumb.jpg")
    
    # Create a small test image
    img = Image.new('RGB', (640, 480), color='blue')
    img.save(background_path)
    
    try:
        create(background_path, thumb_path)
        assert os.path.exists(thumb_path)
    finally:
        # Cleanup
        for f in [background_path, thumb_path]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(tmp_dir)