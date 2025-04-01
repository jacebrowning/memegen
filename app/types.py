from typing import Literal, Union

from PIL.Image import Image as ImageType  # noqa
from PIL.ImageDraw import ImageDraw as DrawType  # noqa
from PIL.ImageFont import FreeTypeFont as FontType  # noqa

Box = tuple[int, int, int, int]
Dimensions = tuple[int, int]
Point = tuple[int, int]
Offset = tuple[float, float]
Align = Union[Literal["left"], Literal["center"], Literal["right"]]
