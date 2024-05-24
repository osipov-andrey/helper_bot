from io import BytesIO
from pathlib import Path
from typing import Tuple

from PIL.Image import Image, new, open

Color = Tuple[int, int, int]
IVORY: Color = (36, 35, 43)


def get_filepath(file_name_: str) -> Path:
    return Path(__file__).parent.absolute().joinpath(file_name_)


def split_vertically(image_: Image) -> Tuple[Image, Image]:
    width, height = image_.size
    center = width // 2
    left_part_ = image_.crop((0, 0, center, height))
    right_part_ = image_.crop((center, 0, width, height))
    return left_part_, right_part_


def expand_image(image_: Image, background_color: Color = IVORY) -> Image:
    width, height = image_.size
    new_height = 2 * height
    new_image = new(image_.mode, (width, new_height), background_color)
    new_image.paste(image_, (0, (new_height - height) // 2))
    return new_image


def get_triptych(source: BytesIO) -> tuple[BytesIO, BytesIO, BytesIO]:
    with open(source) as image:
        left_part, right_part = split_vertically(image)
        exp_image = expand_image(image)

    return (
        _save_image_to_memory(left_part, "left"),
        _save_image_to_memory(right_part, "right"),
        _save_image_to_memory(exp_image, "exp"),
    )


def _save_image_to_memory(img: Image, name: str) -> BytesIO:
    bio = BytesIO()
    bio.name = name
    img.save(bio, "JPEG")
    return bio
