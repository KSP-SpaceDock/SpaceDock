import os.path
from typing import Tuple

from PIL import Image


def create(imagePath: str, thumbnailPath: str, thumbnailSize: Tuple[int, int]) -> None:
    if not os.path.isfile(imagePath):
        return
    im = Image.open(imagePath)
    im.thumbnail(thumbnailSize, Image.ANTIALIAS)
    im.save(thumbnailPath, 'jpeg', quality=50, optimize=True)
