import asyncio
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import aiopath
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

    def stylize(self, text: str, **kwargs) -> str:
        lines = [line for line in kwargs.get("lines", [text]) if line.strip()]

        if self.style == "none":
            return text

        if self.style == "default":
            return text.capitalize() if all(line.islower() for line in lines) else text

        if self.style == "mock":
            return spongemock.mock(text, diversity_bias=0.75, random_seed=0)

        method = getattr(text, self.style or self.__class__.style, None)
        if method:
            return method()

        logger.warning(f"Unsupported text style: {self.style}")
        return text


@datafile
class Overlay:

    x: float = 0.5
    y: float = 0.5
    scale: float = 0.25


@datafile("../templates/{self.id}/config.yml", defaults=True)
class Template:

    id: str
    name: str = ""
    source: Optional[str] = None

    text: list[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.0, anchor_y=0.8)]
    )
    example: list[str] = field(default_factory=lambda: ["your text", "goes here"])

    styles: list[str] = field(default_factory=lambda: [])
    overlay: list[Overlay] = field(default_factory=lambda: [Overlay()])

    def __str__(self):
        return str(self.directory)

    def __lt__(self, other):
        return self.id < other.id

    @property
    def valid(self) -> bool:
        if not settings.DEPLOYED:
            self._update_styles()
            self._update_example()
        return not self.id.startswith("_") and self.image.suffix != ".img"

    def _update_styles(self):
        styles = []
        for path in self.directory.iterdir():
            if not path.stem.startswith("_") and path.stem not in {
                "config",
                settings.DEFAULT_STYLE,
            }:
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

        if "://" in style:
            url = style
            style = utils.text.fingerprint(url)

        self.directory.mkdir(exist_ok=True)
        for path in self.directory.iterdir():
            if path.stem == style:
                return path

        if style == settings.DEFAULT_STYLE:
            logger.debug(f"No default background image for template: {self.id}")
            return self.directory / f"{settings.DEFAULT_STYLE}.img"

        logger.warning(f"Style {style!r} not available for template: {self.id}")
        return self.get_image()

    def jsonify(self, app: Sanic) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "lines": len(self.text),
            "styles": self.styles,
            "blank": app.url_for(
                f"Memes.blank_{settings.DEFAULT_EXT}",
                template_id=self.id,
                _external=True,
                _scheme=settings.SCHEME,
            ),
            "example": self.build_example_url(app),
            "source": self.source,
            "_self": self.build_self_url(app),
        }

    def build_self_url(self, app: Sanic) -> str:
        return app.url_for(
            "Templates.detail",
            id=self.id,
            _external=True,
            _scheme=settings.SCHEME,
        )

    def build_example_url(
        self,
        app: Sanic,
        view_name: str = f"Memes.text_{settings.DEFAULT_EXT}",
        *,
        external: bool = True,
    ) -> str:
        kwargs = {
            "template_id": self.id,
            "text_paths": utils.text.encode(self.example),
            "_external": external,
        }
        if external:
            kwargs["_scheme"] = settings.SCHEME
        url = app.url_for(view_name, **kwargs)
        return utils.urls.clean(url)

    def build_custom_url(
        self,
        request,
        text_lines: list[str],
        *,
        extension: str = "",
        background: str = "",
        style: str = "",
        external: bool = False,
    ):
        if extension in {"jpg", "png"}:
            view_name = f"Memes.text_{extension}"
        else:
            view_name = f"Memes.text_{settings.DEFAULT_EXT}"
        url = request.app.url_for(
            view_name,
            template_id="custom" if self.id == "_custom" else self.id,
            text_paths=utils.text.encode(text_lines),
            _external=True,
            _scheme=settings.SCHEME,
            **utils.urls.params(request, background=background, style=style),
        )
        return utils.urls.clean(url)

    def build_path(
        self,
        text_lines: list[str],
        style: str,
        size: Dimensions,
        watermark: str,
        ext: str,
    ) -> Path:
        slug = utils.text.encode(text_lines)
        variant = str(self.text) + str(style) + str(size) + watermark
        fingerprint = utils.text.fingerprint(variant, prefix="")
        filename = f"{slug}.{fingerprint}.{ext}"
        return Path(self.id) / filename

    @classmethod
    async def create(cls, url: str, *, force=False) -> "Template":
        parts = urlparse(url)
        if parts.netloc == "api.memegen.link":
            logger.debug(f"Handling template URL: {url}")
            id = parts.path.split(".")[0].split("/")[2]
            if id == "custom":
                url = parts.query.removeprefix("background=")
            else:
                return cls.objects.get_or_none(id) or cls.objects.get("_error")

        id = utils.text.fingerprint(url)
        template = cls.objects.get_or_create(id, url)
        if template.image.exists() and not settings.DEBUG and not force:
            logger.info(f"Found background {url} at {template.image}")
            return template

        logger.info(f"Saving background {url} to {template.image}")
        if not await utils.http.download(url, template.image):
            return template

        try:
            utils.images.load(template.image)
        except (OSError, SyntaxError) as e:
            logger.error(e)
            template.image.unlink()

        return template

    async def check(self, style: str, *, force=False) -> bool:
        if not style:
            return True
        if style in self.styles:
            return True
        if "://" not in style:
            logger.error(f"Invalid style for {self.id} template: {style}")
            return False

        url = style
        try:
            _stem, ext = urlparse(url).path.rsplit(".", 1)
        except ValueError:
            logger.error(f"Unable to determine image extension: {url}")
            return False

        filename = utils.text.fingerprint(url, suffix="." + ext)
        path = aiopath.AsyncPath(self.directory) / filename

        if await path.exists() and not settings.DEBUG and not force:
            logger.info(f"Found overlay {url} at {path}")
            return True

        logger.info(f"Saving overlay {url} to {path}")
        if not await utils.http.download(url, path):
            return False

        try:
            await asyncio.to_thread(utils.images.embed, self, Path(path), self.image)
        except (OSError, SyntaxError) as e:
            logger.error(e)
            await path.unlink()

        return await path.exists()

    def delete(self):
        if self.directory.exists():
            shutil.rmtree(self.directory)

    def matches(self, query: str) -> bool:
        example = " ".join(line.lower() for line in self.example)
        return any((query in self.id, query in self.name.lower(), query in example))
