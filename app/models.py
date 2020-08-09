import hashlib
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import aiohttp
from datafiles import datafile, field
from sanic import Sanic
from sanic.log import logger

from . import utils
from .types import Dimensions, Point


@datafile
class Text:

    color: str = "white"

    anchor_x: float = 0.05
    anchor_y: float = 0.05

    angle: float = 0

    scale_x: float = 0.9
    scale_y: float = 0.2

    def get_anchor(self, image_size: Dimensions) -> Point:
        image_width, image_height = image_size
        return int(image_width * self.anchor_x), int(image_height * self.anchor_y)

    def get_size(self, image_size: Dimensions) -> Dimensions:
        image_width, image_height = image_size
        return int(image_width * self.scale_x), int(image_height * self.scale_y)

    def stylize(self, text: str) -> str:
        return text.upper()  # TODO: support mock text


@datafile("../templates/{self.key}/config.yml")
class Template:

    key: str
    name: str = ""
    source: Optional[str] = None
    text: List[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.05, anchor_y=0.75)]
    )
    styles: List[str] = field(default_factory=lambda: ["default"])
    sample: List[str] = field(default_factory=lambda: ["YOUR TEXT", "GOES HERE"])

    @property
    def valid(self) -> bool:
        return bool(self.name and not self.name.startswith("<"))

    @property
    def image(self) -> Path:
        directory = self.datafile.path.parent
        directory.mkdir(exist_ok=True)

        for path in directory.iterdir():
            if path.stem == "default":
                return path

        logger.debug(f"No default background image for template: {self}")
        return directory / "default.img"

    def jsonify(self, app: Sanic) -> Dict:
        return {
            "name": self.name,
            "styles": [s for s in self.styles if s != "default"],
            "blank": app.url_for("images.blank", key=self.key, _external=True),
            "sample": self.build_sample_url(app),
            "source": self.source,
            "_self": app.url_for("templates.detail", key=self.key, _external=True),
        }

    def build_sample_url(self, app: Sanic) -> str:
        return app.url_for(
            "images.text",
            key=self.key,
            slug=utils.text.encode(self.sample),
            _external=True,
        )

    @classmethod
    async def create(cls, url: str) -> "Template":
        key = "_custom-" + hashlib.sha1(url.encode()).hexdigest()
        template = cls.objects.get_or_create(key, url)

        logger.info(f"Saving {url} to {template.image}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    f = await aiofiles.open(template.image, mode="wb")
                    await f.write(await response.read())
                    await f.close()

        return template
