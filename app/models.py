import hashlib
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import aiofiles
import aiohttp
from aiohttp.client_exceptions import ClientConnectionError, InvalidURL
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

    def stylize(self, text: str) -> str:
        if self.style == "none":
            return text

        if self.style == "default":
            return text.capitalize() if text.islower() else text

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
    text: list[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.0, anchor_y=0.8)]
    )
    styles: list[str] = field(default_factory=lambda: [])
    example: list[str] = field(default_factory=lambda: ["your text", "goes here"])

    def __str__(self):
        return str(self.directory)

    def __lt__(self, other):
        return self.key < other.key

    @property
    def valid(self) -> bool:
        if not settings.DEPLOYED:
            self._update_styles()
            self._update_example()
        return not self.key.startswith("_") and self.image.suffix != ".img"

    def _update_styles(self):
        styles = []
        for path in self.directory.iterdir():
            if path.stem not in {"config", settings.DEFAULT_STYLE}:
                styles.append(path.stem)
        styles.sort()
        if styles != self.styles:
            self.styles = styles

    def _update_example(self):
        for line in self.example:
            if line and not line.isupper():
                return
        self.example = [line.lower() for line in self.example]

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
            return self.directory / f"{settings.DEFAULT_STYLE}.img"
        else:
            logger.warning(f"Style {style!r} not available for {self.key}")
            return self.get_image()

    def jsonify(self, app: Sanic) -> dict:
        return {
            "name": self.name,
            "key": self.key,
            "lines": len(self.text),
            "styles": self.styles,
            "blank": app.url_for(
                f"images.blank_{settings.DEFAULT_EXT}",
                template_key=self.key,
                _external=True,
                _scheme=settings.SCHEME,
            ),
            "example": self.build_example_url(app),
            "source": self.source,
            "_self": self.build_self_url(app),
        }

    def build_self_url(self, app: Sanic) -> str:
        return app.url_for(
            "templates.detail",
            key=self.key,
            _external=True,
            _scheme=settings.SCHEME,
        )

    def build_example_url(
        self,
        app: Sanic,
        view_name: str = f"images.text_{settings.DEFAULT_EXT}",
        *,
        external: bool = True,
    ) -> str:
        kwargs = {
            "template_key": self.key,
            "text_paths": utils.text.encode(self.example),
            "_external": external,
        }
        if external:
            kwargs["_scheme"] = settings.SCHEME
        url = app.url_for(view_name, **kwargs)
        url = self._drop_trailing_spaces(url)
        return url

    def build_custom_url(
        self,
        app: Sanic,
        text_lines: list[str],
        *,
        extension: str = "",
        background: str = "",
        external: bool = False,
    ):
        if extension in {"jpg", "png"}:
            view_name = f"images.text_{extension}"
        else:
            view_name = f"images.text_{settings.DEFAULT_EXT}"
        url = app.url_for(
            view_name,
            template_key="custom" if self.key == "_custom" else self.key,
            text_paths=utils.text.encode(text_lines),
            _external=True,
            _scheme=settings.SCHEME,
        )
        url = self._drop_trailing_spaces(url)
        if background:
            url += "?background=" + background
        return url

    @staticmethod
    def _drop_trailing_spaces(url: str) -> str:
        while "/_." in url:
            url = url.replace("/_.", ".")
        return url

    @classmethod
    async def create(cls, url: str) -> "Template":
        parts = urlparse(url)
        if "memegen.link" in parts.netloc:
            logger.debug(f"Handling template URL: {url}")
            key = parts.path.split(".")[0].split("/")[2]
            if key == "custom":
                url = parts.query.removeprefix("background=")
            else:
                return cls.objects.get_or_none(key) or cls.objects.get("_error")

        key = "_custom-" + hashlib.sha1(url.encode()).hexdigest()
        template = cls.objects.get_or_create(key, url)
        if template.image.exists() and not settings.DEBUG:
            logger.info(f"Found background {url} at {template.image}")

        else:
            logger.info(f"Saving background {url} to {template.image}")
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            template.directory.mkdir(exist_ok=True)
                            f = await aiofiles.open(template.image, mode="wb")  # type: ignore
                            await f.write(await response.read())
                            await f.close()
                        else:
                            logger.error(f"{response.status} response from {url}")
                except (InvalidURL, ClientConnectionError):
                    logger.error(f"Invalid response from {url}")

        if template.image.exists():
            try:
                utils.images.load(template.image)
            except OSError as e:
                logger.error(e)
                template.image.unlink()

        return template

    def delete(self):
        shutil.rmtree(self.directory)
