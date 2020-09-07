import hashlib
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import aiohttp
from datafiles import datafile, field
from sanic import Sanic
from sanic.log import logger
from spongemock import spongemock

from . import settings, utils
from .types import Dimensions, Point


@datafile
class Text:

    color: str = "white"
    style: str = "upper"

    anchor_x: float = 0.0
    anchor_y: float = 0.0

    angle: float = 0

    scale_x: float = 1.0
    scale_y: float = 0.2

    def get_anchor(self, image_size: Dimensions) -> Point:
        image_width, image_height = image_size
        return int(image_width * self.anchor_x), int(image_height * self.anchor_y)

    def get_size(self, image_size: Dimensions) -> Dimensions:
        image_width, image_height = image_size
        return int(image_width * self.scale_x), int(image_height * self.scale_y)

    def stylize(self, text: str) -> str:
        if self.style == "none":
            return text

        if self.style == "mock":
            return spongemock.mock(text, diversity_bias=0.75, random_seed=0)

        method = getattr(text, self.style or self.__class__.style, None)
        if method:
            return method()

        logger.warning(f"Unsupported text style: {self.style}")
        return text


@datafile("../templates/{self.key}/config.yml", defaults=True)
class Template:

    key: str
    name: str = ""
    source: Optional[str] = None
    text: List[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.0, anchor_y=0.8)]
    )
    styles: List[str] = field(default_factory=lambda: [settings.DEFAULT_STYLE])
    sample: List[str] = field(default_factory=lambda: ["YOUR TEXT", "GOES HERE"])

    def __str__(self):
        return str(self.directory)

    @property
    def valid(self) -> bool:
        return not self.key.startswith("_") and self.image.suffix != ".img"

    @property
    def directory(self) -> Path:
        return self.datafile.path.parent

    @property
    def image(self) -> Path:
        return self.get_image()

    def get_image(self, style: str = "") -> Path:
        style = style or settings.DEFAULT_STYLE

        self.directory.mkdir(exist_ok=True)
        for path in self.directory.iterdir():
            if path.stem == style:
                return path

        if style == settings.DEFAULT_STYLE:
            logger.debug(f"No default background image for template: {self.key}")
            return self.directory / "default.img"
        else:
            logger.warning(f"Style {style!r} not available for {self.key}")
            return self.get_image()

    def jsonify(self, app: Sanic) -> Dict:
        return {
            "name": self.name,
            "key": self.key,
            "styles": [s for s in self.styles if s != settings.DEFAULT_STYLE],
            "blank": app.url_for(
                f"images.blank_{settings.DEFAULT_EXT}",
                template_key=self.key,
                _external=True,
                _scheme="https" if settings.DEPLOYED else "http",
            ),
            "sample": self.build_sample_url(app),
            "source": self.source,
            "_self": self.build_self_url(app),
        }

    def build_self_url(self, app: Sanic) -> str:
        return app.url_for(
            "templates.detail",
            key=self.key,
            _external=True,
            _scheme="https" if settings.DEPLOYED else "http",
        )

    def build_sample_url(
        self,
        app: Sanic,
        view_name: str = f"images.text_{settings.DEFAULT_EXT}",
        *,
        external: bool = True,
    ) -> str:
        kwargs = {
            "template_key": self.key,
            "text_paths": utils.text.encode(self.sample),
            "_external": external,
        }
        if external:
            kwargs["_scheme"] = "https" if settings.DEPLOYED else "http"
        return app.url_for(view_name, **kwargs)

    def build_custom_url(
        self,
        app: Sanic,
        text_lines: List[str],
        *,
        extension: str = "",
        background: str = "",
        external: bool = False,
    ):
        url = app.url_for(
            f"images.text_{extension or settings.DEFAULT_EXT}",
            template_key="custom" if self.key == "_custom" else self.key,
            text_paths=utils.text.encode(text_lines),
            _external=True,
            _scheme="https" if settings.DEPLOYED else "http",
        )
        if background:
            url += "?background=" + background
        return url

    @classmethod
    async def create(cls, url: str) -> "Template":
        key = "_custom-" + hashlib.sha1(url.encode()).hexdigest()
        template = cls.objects.get_or_create(key, url)

        if template.image.exists() and not settings.DEBUG:
            logger.info(f"Found {url} at {template.image}")
            return template

        logger.info(f"Saving {url} to {template.image}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    template.directory.mkdir(exist_ok=True)
                    f = await aiofiles.open(template.image, mode="wb")
                    await f.write(await response.read())
                    await f.close()
                else:
                    logger.info(f"{response.status} response from {url}")

        return template
