import asyncio
import shutil
from contextlib import suppress
from functools import cached_property
from pathlib import Path

import aiopath
from datafiles import datafile, field
from furl import furl
from sanic import Request
from sanic.log import logger

from .. import settings, utils
from ..types import Dimensions
from .overlay import Overlay
from .text import Text

DEFAULT_TEXT = [
    Text(start=0.0, stop=1.0),
    Text(start=0.0, stop=1.0, anchor_x=0.0, anchor_y=0.8),
]
ANIMATED_TEXT = [
    Text(start=0.2, stop=1.0),
    Text(start=0.6, stop=1.0, anchor_x=0.0, anchor_y=0.8),
]

DEFAULT_EXAMPLE = [
    "Top Line",
    "Bottom Line",
]


@datafile("../../templates/{self.id}/config.yml", defaults=True)
class Template:

    id: str
    name: str = ""
    source: str | None = None

    text: list[Text] = field(default_factory=lambda: DEFAULT_TEXT)
    example: list[str] = field(default_factory=lambda: DEFAULT_EXAMPLE)

    overlay: list[Overlay] = field(default_factory=lambda: [Overlay()])

    def __str__(self):
        return str(self.directory)

    def __lt__(self, other):
        return self.id < other.id

    @cached_property
    def valid(self) -> bool:
        if not settings.DEPLOYED:
            self._update_example()
            self.datafile.save()
        return (
            not self.id.startswith("_")
            and self.image.suffix != settings.PLACEHOLDER_SUFFIX
        )

    def _update_example(self):
        for line in self.example:
            if line and not line.isupper():
                return
        self.example = [line.lower() for line in self.example]

    @cached_property
    def styles(self):
        styles = []
        for path in self.directory.iterdir():
            if not path.stem[0] in {".", "_"} and path.stem not in {
                "config",
                settings.DEFAULT_STYLE,
            }:
                styles.append(path.stem)
        if styles or self.overlay != [Overlay()]:
            styles.append("default")
        styles.sort()
        return styles

    @cached_property
    def directory(self) -> Path:
        return self.datafile.path.parent

    @cached_property
    def image(self) -> Path:
        return self.get_image()

    def get_image(self, style: str = "", *, animated: bool = False) -> Path:
        style = style or settings.DEFAULT_STYLE
        if style == settings.DEFAULT_STYLE and animated:
            style = "animated"

        if utils.urls.schema(style):
            url = style
            style = utils.text.fingerprint(url)

        self.directory.mkdir(exist_ok=True)
        for path in self.directory.iterdir():
            if path.stem == style and path.suffix != settings.PLACEHOLDER_SUFFIX:
                return path

        if style == settings.DEFAULT_STYLE:
            logger.debug(f"No default background image for template: {self.id}")
            return self.directory / (
                settings.DEFAULT_STYLE + settings.PLACEHOLDER_SUFFIX
            )

        if style == "animated":
            logger.info(f"Using default image to animate static template: {self.id}")
        else:
            logger.warning(f"Style {style!r} not available for template: {self.id}")

        return self.get_image()

    def jsonify(self, request: Request) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "lines": len(self.text),
            "overlays": len(self.overlay) if self.styles else 0,
            "styles": self.styles,
            "blank": request.app.url_for(
                "images.blank",
                template_filename=self.id + "." + settings.DEFAULT_EXTENSION,
                _external=True,
                _scheme=settings.SCHEME,
            ),
            "example": {
                "text": self.example if any(self.example) else [],
                "url": self.build_example_url(request),
            },
            "source": self.source,
            "_self": self.build_self_url(request),
        }

    def build_self_url(self, request: Request) -> str:
        return request.app.url_for(
            "templates.detail",
            id=self.id,
            _external=True,
            _scheme=settings.SCHEME,
        )

    def build_example_url(
        self,
        request: Request,
        *,
        extension: str = settings.DEFAULT_EXTENSION,
        external: bool = True,
    ) -> str:
        kwargs = {
            "template_id": self.id,
            "text_filepath": utils.text.encode(self.example) + "." + extension,
            "_external": external,
        }
        if external:
            kwargs["_scheme"] = settings.SCHEME
        url = request.app.url_for("images.text", **kwargs)
        return utils.urls.clean(url)

    def build_custom_url(
        self,
        request: Request,
        text_lines: list[str],
        *,
        extension: str = settings.DEFAULT_EXTENSION,
        background: str = "",
        style: str = "",
        font: str = "",
    ):
        if extension not in settings.ALLOWED_EXTENSIONS:
            extension = settings.DEFAULT_EXTENSION
        if style == settings.DEFAULT_STYLE:
            style = ""
        url = request.app.url_for(
            "images.text",
            template_id="custom" if self.id == "_custom" else self.id,
            text_filepath=utils.text.encode(text_lines) + "." + extension,
            _external=True,
            _scheme=settings.SCHEME,
            **utils.urls.params(background=background, style=style, font=font),
        )
        return utils.urls.clean(url)

    def build_path(
        self,
        text_lines: list[str],
        font_name: str,
        style: str,
        size: Dimensions,
        watermark: str,
        extension: str,
        frames: int = 0,
    ) -> Path:
        slug = utils.text.encode(text_lines)
        variant = str(self.text) + font_name + style + str(size) + watermark
        if frames:
            variant += str(frames)
        fingerprint = utils.text.fingerprint(variant, prefix="")
        filename = f"{slug}.{fingerprint}.{extension}"
        return Path(self.id) / filename

    @classmethod
    async def create(cls, url: str, *, force=False) -> "Template":
        try:
            parsed = furl(url)
        except ValueError as e:
            logger.error(e)
            return cls.objects.get("_error")

        if parsed.netloc and "memegen.link" in parsed.netloc:
            logger.info(f"Handling template URL: {url}")
            if len(parsed.path.segments) > 1:
                id = Path(parsed.path.segments[1]).stem
                if id != "custom":
                    return cls.objects.get_or_none(id) or cls.objects.get("_error")
                background = parsed.args.get("background")
                if not background:
                    return cls.objects.get("_error")
                url = background
                try:
                    parsed = furl(url)
                except ValueError as e:
                    logger.error(e)
                    return cls.objects.get("_error")

        id = utils.text.fingerprint(url)
        template = cls.objects.get_or_create(id, url)

        suffix = Path(str(parsed.path)).suffix
        if not suffix or len(suffix) > 10:
            logger.warning(f"Unable to determine image extension: {url}")
            suffix = settings.PLACEHOLDER_SUFFIX

        filename = "default" + suffix
        path = aiopath.AsyncPath(template.directory) / filename

        if await path.exists() and not settings.DEBUG and not force:
            logger.info(f"Found background {url} at {path}")
            return template

        logger.info(f"Saving background {url} to {path}")
        if not await utils.http.download(url, path):
            return template

        try:
            await asyncio.to_thread(utils.images.load, Path(path))
        except utils.images.EXCEPTIONS as e:
            logger.error(e)
            await path.unlink(missing_ok=True)

        return template

    async def check(self, style: str, *, force=False) -> bool:
        if style in {"", None, settings.DEFAULT_STYLE}:
            return True

        if style in self.styles:
            return True

        if not utils.urls.schema(style):
            logger.error(f"Invalid style for {self.id} template: {style}")
            return False

        filename = utils.text.fingerprint(style, suffix=self.image.suffix)
        path = aiopath.AsyncPath(self.directory) / filename
        if await path.exists() and not settings.DEBUG and not force:
            logger.info(f"Found overlay {style} at {path}")
            return True

        urls = style.split(",")
        logger.info(f"Embeding {len(urls)} overlay image(s) onto {path}")
        await asyncio.to_thread(shutil.copy, self.image, path)

        embedded = 0
        for index, url in enumerate(urls):
            success = await self._embed(index, url, path, force)
            if success:
                embedded += 1

        if len(urls) == 1 and not embedded:
            await path.unlink()

        return embedded == len(urls)

    async def _embed(
        self, index: int, url: str, background: aiopath.AsyncPath, force: bool
    ) -> bool:
        if url.strip() in {"", settings.DEFAULT_STYLE}:
            return True

        suffix = Path(str(furl(url).path)).suffix
        if not suffix:
            logger.warning(f"Unable to determine image extension: {url}")
            suffix = ".png"

        filename = utils.text.fingerprint(url, prefix="_embed-", suffix=suffix)
        foreground = aiopath.AsyncPath(self.directory) / filename

        if await foreground.exists() and not settings.DEBUG and not force:
            logger.info(f"Found overlay {url} at {foreground}")
        else:
            logger.info(f"Saving overlay {url} to {foreground}")
            await utils.http.download(url, foreground)

        try:
            await asyncio.to_thread(
                utils.images.embed, self, index, Path(foreground), Path(background)
            )
        except utils.images.EXCEPTIONS as e:
            logger.error(e)
            await foreground.unlink(missing_ok=True)

        return await foreground.exists()

    @property
    def animated(self):
        if self.text == DEFAULT_TEXT or self.text == ANIMATED_TEXT:
            return False
        return any(text.animated for text in self.text)

    def animate(self, start: str = "0.2,0.6", stop: str = "1.0,1.0"):
        try:
            starts = [float(value) for value in start.split(",") if value]
            stops = [float(value) for value in stop.split(",") if value]
        except ValueError:
            logger.error(f"Invalid text animation: {start=} {stop=}")
            return

        with suppress(IndexError):
            for index, value in enumerate(starts):
                self.text[index].start = value

        with suppress(IndexError):
            for index, value in enumerate(stops):
                self.text[index].stop = value

        if starts or stops:
            logger.info(f"Updated {self} with: {starts=} {stops=}")

    def clean(self):
        for path in self.directory.iterdir():
            if path.stem not in {"config", "default"}:
                path.unlink()

    def delete(self):
        if self.directory.exists():
            shutil.rmtree(self.directory)

    def matches(self, query: str) -> bool:
        example = " ".join(line.lower() for line in self.example)
        return any((query in self.id, query in self.name.lower(), query in example))
