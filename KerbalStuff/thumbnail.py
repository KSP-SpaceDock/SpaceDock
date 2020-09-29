import os.path

from PIL import Image

from KerbalStuff.config import _cfg, _cfgi, site_logger


def create(background_path: str, thumbnail_path: str) -> None:
    if not os.path.isfile(background_path):
        return

    size_str = _cfg('thumbnail_size')
    if not size_str:
        size_str = "320x195"
    size_str_tuple = size_str.split('x')
    size = (int(size_str_tuple[0]), int(size_str_tuple[1]))

    quality = _cfgi('thumbnail_quality')
    # Docs say the quality shouldn't be above 95:
    # https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg
    if not quality or not (0 <= quality <= 95):
        quality = 80

    im = Image.open(background_path)

    # We want to resize the image to the desired size in the least costly way,
    # while not distorting it. This means we first check which side needs _less_ rescaling to reach
    # the target size. After that we scale it down while keeping the original aspect ratio.
    x_ratio = abs(im.width/size[0])
    y_ratio = abs(im.height/size[1])

    if x_ratio < y_ratio:
        im = im.resize((size[0], round(im.height/x_ratio)), Image.LANCZOS)
    else:
        im = im.resize((round(im.width/y_ratio), size[1]), Image.LANCZOS)

    # Now there's one pair of edges that already has the target length (height or width).
    # Next step is cropping the thumbnail out of the center of the down-scaled base image,
    # to also downsize the other edge pair without distorting the image.
    # We basically define the upper left and the lower right corner of the area to crop out here,
    # but we have to serve them separately (better: in one 4-tuple) to im.crop():
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop
    box_left = round(0.5 * (im.width - size[0]))
    box_upper = round(0.5 * (im.height - size[1]))
    box_right = round(0.5 * (im.width + size[0]))
    box_lower = round(0.5 * (im.height + size[1]))
    im = im.crop((box_left, box_upper, box_right, box_lower))

    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(thumbnail_path, 'jpeg', quality=quality, optimize=True)


def get_or_create(background_url: str) -> str:
    storage = _cfg('storage')
    if not storage:
        return background_url

    (background_directory, background_file_name) = os.path.split(background_url)

    thumb_file_name = os.path.splitext(background_file_name)[0] + '.jpg'
    thumb_url = os.path.join(background_directory, 'thumb_' + thumb_file_name)

    thumb_disk_path = os.path.join(storage, thumb_url.replace('/content/', ''))
    background_disk_path = os.path.join(storage, background_url.replace('/content/', ''))

    if not os.path.isfile(thumb_disk_path):
        try:
            create(background_disk_path, thumb_disk_path)
        except Exception as e:
            site_logger.exception(e)
            return background_url
    return thumb_url
