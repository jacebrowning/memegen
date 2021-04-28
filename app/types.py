from dataclasses import dataclass
from typing import Optional

from sanic.log import logger
from spongemock import spongemock

from . import settings

Box = tuple[int, int, int, int]
Dimensions = tuple[int, int]
Point = tuple[int, int]
Offset = tuple[int, int]


@dataclass
class Text:

    color: str = "white"
    style: str = "upper"

    anchor_x: float = 0.0
    anchor_y: float = 0.0

    angle: float = 0

    scale_x: float = 1.0
    scale_y: float = 0.2

    @classmethod
    def get_preview(cls) -> "Text":
        return cls(
            color="#80808085",
            anchor_x=0.075,
            anchor_y=0.05,
            angle=10,
            scale_x=0.75,
            scale_y=0.75,
        )

    @classmethod
    def get_watermark(cls) -> "Text":
        return cls(color="#FFFFFF85")

    def get_anchor(self, image_size: Dimensions, watermark: str = "") -> Point:
        image_width, image_height = image_size
        anchor = int(image_width * self.anchor_x), int(image_height * self.anchor_y)
        if watermark and self.anchor_x <= 0.1 and self.anchor_y >= 0.8:
            anchor = anchor[0], anchor[1] - settings.WATERMARK_HEIGHT // 3
        return anchor

    def get_size(self, image_size: Dimensions) -> Dimensions:
        image_width, image_height = image_size
        size = int(image_width * self.scale_x), int(image_height * self.scale_y)
        return size

    def get_stroke(self, width: int, color: str = "black") -> tuple[int, str]:
        if self.color == "black":
            width = 1
            color = "#FFFFFF85"
        elif "#" in self.color:
            width = 1
            color = "#000000" + self.color[-2:]
        return width, color

    def stylize(self, text: str, **kwargs) -> tuple[str, bool]:
        lines = [line for line in kwargs.get("lines", [text]) if line.strip()]

        if self.style == "none":
            return text, False

        if self.style in {"default", "thin"}:
            text = text.capitalize() if all(line.islower() for line in lines) else text
            return text, self.style == "thin"

        if self.style == "mock":
            return spongemock.mock(text, diversity_bias=0.75, random_seed=0), False

        method = getattr(text, self.style or self.__class__.style, None)
        if method:
            return method(), False

        logger.warning(f"Unsupported text style: {self.style}")
        return text, False


@dataclass
class Overlay:

    center_x: float = 0.5
    center_y: float = 0.5
    scale: float = 0.25

    def get_size(self, background_size: Dimensions) -> Dimensions:
        background_width, background_height = background_size
        dimension = min(
            int(background_width * self.scale),
            int(background_height * self.scale),
        )
        return dimension, dimension

    def get_box(
        self, background_size: Dimensions, foreground_size: Optional[Dimensions] = None
    ) -> Box:
        background_width, background_height = background_size
        if foreground_size is None:
            foreground_size = self.get_size(background_size)
        foreground_width, foreground_height = foreground_size
        box = (
            int(background_width * self.center_x - foreground_width / 2),
            int(background_height * self.center_y - foreground_height / 2),
            int(background_width * self.center_x + foreground_width / 2),
            int(background_height * self.center_y + foreground_height / 2),
        )
        return box
