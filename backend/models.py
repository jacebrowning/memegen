from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import aiofiles
import aiohttp
import log
from aiofiles import os
from datafiles import converters, datafile
from sanic import Sanic

from backend import settings


@dataclass
class Text:

    color: str = "white"

    anchor_x: float = 0.1
    anchor_y: float = 0.1

    angle: float = 0

    scale_x: float = 0.8
    scale_y: float = 0.2


@datafile("../templates/{self.key}/config.yml")
class Template:

    key: str
    name: str = ""
    source: Optional[str] = None
    text: List[Text] = field(default_factory=lambda: [Text(), Text()])
    styles: List[str] = field(default_factory=lambda: ["default"])
    sample: List[str] = field(default_factory=lambda: ["YOUR TEXT", "GOES HERE"])

    @property
    def valid(self) -> bool:
        return bool(self.name and not self.name.startswith("<"))

    def jsonify(self, app: Sanic) -> Dict:
        return {
            "name": self.name,
            "styles": [s for s in self.styles if s != "default"],
            "blank": app.url_for("image_blank", key=self.key, _external=True),
            "sample": self.build_sample_url(app),
            "source": self.source,
            "_self": app.url_for("templates_detail", key=self.key, _external=True),
        }

    def build_sample_url(self, app: Sanic) -> str:
        return app.url_for(
            "image_text",
            key=self.key,
            lines="/".join(self._encode(*self.sample)),
            _external=True,
        )

    async def render(self, *lines) -> Path:
        text = "/".join(lines)
        image_path = Path(f"images/{self.key}/{text}.jpg")
        image_path.parent.mkdir(parents=True, exist_ok=True)

        background_image_path = self._get_background_image_path()
        background_image_url = f"{settings.IMAGES_URL}/{background_image_path}"
        image_url = f"https://memegen.link/custom/{text}.jpg?alt={background_image_url}"
        log.debug(f"Fetching image: {image_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    f = await aiofiles.open(image_path, mode="wb")
                    await f.write(await response.read())
                    await f.close()

        return image_path

    def _get_background_image_path(self, name="default") -> Path:
        for ext in ["png", "jpg"]:
            path = Path("templates", self.key, f"default.{ext}")
            if path.exists():
                return path
        raise ValueError(f"No background image for template: {self}")

    @staticmethod
    def _encode(*lines: str) -> Iterator[str]:
        for line in lines:
            if line:
                yield line.lower().replace(" ", "_").replace("?", "~q")
            else:
                yield "_"
