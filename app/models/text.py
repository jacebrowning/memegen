import re
from dataclasses import dataclass

from sanic.log import logger
from spongemock import spongemock

from .. import settings
from ..types import Dimensions, Point


def alpha(value: float) -> str:
    return hex(int(255 * value))[2:].upper()


@dataclass
class Text:

    style: str = "upper"
    color: str = "white"
    font: str = settings.DEFAULT_FONT

    anchor_x: float = 0.0
    anchor_y: float = 0.0

    angle: float = 0

    scale_x: float = 1.0
    scale_y: float = 0.2

    align: str = "center"

    start: float = 0.0
    stop: float = 1.0

    @classmethod
    def get_preview(cls) -> "Text":
        return cls(
            color="#808080" + alpha(0.375),
            anchor_x=0.075,
            anchor_y=0.05,
            angle=10,
            scale_x=0.75,
            scale_y=0.75,
        )

    @classmethod
    def get_error(cls) -> "Text":
        return cls(color="yellow", anchor_x=0.5)

    @classmethod
    def get_watermark(cls) -> "Text":
        return cls(color="#FFFFFF" + alpha(0.75))

    @property
    def animated(self) -> bool:
        return not (self.start == 0.0 and self.stop == 1.0)

    def get_anchor(self, image_size: Dimensions, watermark: str = "") -> Point:
        image_width, image_height = image_size
        anchor = int(image_width * self.anchor_x), int(image_height * self.anchor_y)
        if watermark and self.anchor_x <= 0.1 and self.anchor_y >= 0.8:
            anchor = anchor[0], anchor[1] - settings.WATERMARK_HEIGHT // 2
        return anchor

    def get_size(self, image_size: Dimensions) -> Dimensions:
        image_width, image_height = image_size
        size = int(image_width * self.scale_x), int(image_height * self.scale_y)
        return size

    def get_stroke(self, width: int) -> tuple[int, str]:
        if self.color == "black":
            width = 1
            color = "#FFFFFF" + alpha(0.5)
        elif "#" in self.color:
            width = 1
            color = "#000000" + self.color[-2:]
        else:
            color = "black"
        return width, color

    def normalize(self, text: str | None) -> str:
        if text is None:
            return ""
        if self.style not in {"none", "default", "mock"}:
            return text.lower()
        return text

    def stylize(self, text: str, **kwargs) -> str:
        lines = [line for line in kwargs.get("lines", [text]) if line.strip()]

        if self.style == "none":
            return text

        if self.style == "default":
            text = text.capitalize() if all(line.islower() for line in lines) else text
            text = re.sub(r"\bi\b", "I", text)
            return text

        if self.style == "mock":
            return spongemock.mock(text, diversity_bias=0.75, random_seed=0)

        method = getattr(text, self.style or self.__class__.style, None)
        if method:
            return method()

        logger.warning(f"Unsupported text style: {self.style}")
        return text
