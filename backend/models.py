from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import aiofiles
import aiohttp
import log
from aiofiles import os
from datafiles import converters, datafile
from sanic import Sanic


class UpperString(converters.String):
    @classmethod
    def to_preserialization_data(cls, python_value, **kwargs):
        line = super().to_preserialization_data(python_value, **kwargs)
        return line.upper()

    @classmethod
    def to_python_value(cls, deserialized_data, **kwargs):
        line = super().to_python_value(deserialized_data, **kwargs)
        return line.lower().replace(" ", "_")


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
    sample: List[UpperString] = field(
        default_factory=lambda: [UpperString("YOUR TEXT"), UpperString("GOES HERE")]
    )

    @property
    def valid(self) -> bool:
        return bool(self.name and not self.name.startswith("<"))

    def json(self, app: Sanic) -> Dict:
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
        print(f"TODO: render lines: {lines}")
        # return self._get_background_image_path()

        path = Path("images/" + self._get_v1_path(lines))
        path.parent.mkdir(parents=True, exist_ok=True)

        url = "https://memegen.link/" + self._get_v1_path(lines)
        log.debug(f"Fetching image: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    f = await aiofiles.open(path, mode="wb")
                    await f.write(await response.read())
                    await f.close()

        return path

    def _get_v1_path(self, lines) -> str:
        paths = "/".join(lines)
        return f"{self.key}/{paths}.jpg"

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
                yield line.replace("?", "~q")
            else:
                yield "_"
