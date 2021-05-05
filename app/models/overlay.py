from dataclasses import dataclass
from typing import Optional

from ..types import Box, Dimensions


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
