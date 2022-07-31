import asyncio
import shutil
from contextlib import suppress
from functools import cached_property
from pathlib import Path

import aiopath
from datafiles import datafile, field, frozen
from furl import furl
from sanic import Request
from sanic.log import logger

from .. import settings, utils
from ..types import Dimensions
from .overlay import Overlay
from .text import Text


@datafile("../../templates/{self.id}/config.yml", defaults=True)
class Template:

    id: str
    name: str = ""
    source: str | None = None

    text: list[Text] = field(
        default_factory=lambda: [Text(), Text(anchor_x=0.0, anchor_y=0.8)]
    )

    example: list[str] = field(default_factory=lambda: ["Top Line", "Bottom Line"])

    overlay: list[Overlay] = field(default_factory=lambda: [Overlay()])

    def __str__(self):
        return str(self.directory)

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self):
        return hash(self.id)

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
            if path.stem[0] in {".", "_"}:
                continue
            if path.stem not in {"config", "default"}:
                styles.append(path.stem)
            elif path.name == "default.gif":
                styles.append("animated")
        if styles or self.overlay != [Overlay()]:
            styles.append("default")
        styles.sort()
        return styles

    @cached_property
    def animated_image(self):
        return "animated" in self.styles

    @cached_property
    def animated_text(self):
        return any(text.animated for text in self.text)

    @cached_property
    def directory(self) -> Path:
        return self.datafile.path.parent

    @cached_property
    def image(self) -> Path:
        return self.get_image()

    def get_image(self, style: str = "default", *, animated=False) -> Path:
        level = 20 if (style != "default" or animated is True) else 10

        style = style or "default"
        logger.log(level, f"Getting background image: {self.id=} {style=} {animated=}")
        if style == "animated":
            style = "default"
            animated = True

        url = ""
        if utils.urls.schema(style):
            url = style
            style = utils.text.fingerprint(f"{url}{self.overlay}")

        self.directory.mkdir(exist_ok=True)
        paths: list[Path] = []
        for path in self.directory.iterdir():
            if path.stem == style and path.suffix != settings.PLACEHOLDER_SUFFIX:
                paths.append(path)

        if animated:
            for path in paths:
                if path.suffix == ".gif":
                    logger.log(level, f"Matched path by suffix: {path}")
                    return path

            for path in paths:
                if path.stem == style:
                    logger.log(level, f"Matched path by stem: {path}")
                    return path
        else:
            for path in paths:
                if path.suffix != ".gif":
                    logger.log(level, f"Matched path by suffix: {path}")
                    return path

        path = self.directory / "default.gif"
        if path.exists():
            logger.log(level, f"Matched path by default: {path}")
            return path

        if style == "default" and not animated:
            logger.info(f"No default background image for template: {self.id}")
            return self.directory / ("default" + settings.PLACEHOLDER_SUFFIX)

        if animated:
            logger.info(f"Using static image to animate template: {self.id}")
        else:
            logger.warning(
                f"Style {url or style!r} not available for template: {self.id}"
            )

        return self.get_image()

    def jsonify(self, request: Request) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "lines": len(self.text),
            "overlays": len(self.overlay) if self.styles else 0,
            "styles": self.styles,
            "blank": request.app.url_for(
                "images.detail_blank",
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
        extension: str = "",
        external: bool = True,
    ) -> str:
        extension = extension or self._extension
        kwargs = {
            "template_id": self.id,
            "text_filepath": utils.text.encode(self.example) + "." + extension,
            "_external": external,
        }
        if external:
            kwargs["_scheme"] = settings.SCHEME
        url = request.app.url_for("images.detail_text", **kwargs)
        return utils.urls.clean(url)

    def build_custom_url(
        self,
        request: Request,
        text_lines: list[str],
        *,
        extension: str = "",
        background: str = "",
        style: str = "",
        font: str = "",
    ):
        with suppress(IndexError):
            for index, text in enumerate(self.text):
                text_lines[index] = text.normalize(text_lines[index])
        if not extension and background:
            url = furl(background)
            extension = url.path.segments[-1].split(".")[-1]
        if extension not in settings.ALLOWED_EXTENSIONS:
            extension = self._extension
        if style == "default":
            style = ""
        elif style == "animated":
            extension = "gif"
            style = ""
        url = request.app.url_for(
            "images.detail_text",
            template_id="custom" if self.id == "_custom" else self.id,
            text_filepath=utils.text.encode(text_lines) + "." + extension,
            _external=True,
            _scheme=settings.SCHEME,
            **utils.urls.params(background=background, style=style, font=font),
        )
        return utils.urls.clean(url)

    @property
    def _extension(self) -> str:
        return "gif" if self.animated_image else settings.DEFAULT_EXTENSION

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
        if self.overlay != [Overlay()]:
            variant += str(self.overlay)
        if frames:
            variant += str(frames)
        fingerprint = utils.text.fingerprint(variant, prefix="")
        filename = f"{slug}.{fingerprint}.{extension}"
        return Path(self.id) / filename

    @classmethod
    async def create(
        cls, url: str, *, layout: str = "default", lines: int = 2, force=False
    ) -> "Template":
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
        if layout != "default":
            id += f"-{layout}{lines}"
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

        if layout == "top":
            with frozen(template):
                template.text = []
                for index in range(lines):
                    text = Text(
                        style="none",
                        color="black",
                        font="thin",
                        anchor_x=0,
                        anchor_y=index * 0.1,
                        scale_x=1.0,
                        scale_y=0.2 / lines,
                        align="left",
                    )
                    template.text.append(text)

            await asyncio.to_thread(utils.images.add_top_padding, Path(path))

        return template

    async def check(self, style: str, *, animated=False, force=False) -> bool:
        if style in {None, "", "default"}:
            return True

        if style in self.styles:
            return True

        if not utils.urls.schema(style):
            logger.error(f"Invalid style for {self.id} template: {style}")
            return False

        image = self.get_image(animated=animated)
        filename = utils.text.fingerprint(f"{style}{self.overlay}", suffix=image.suffix)
        path = aiopath.AsyncPath(self.directory) / filename
        if await path.exists() and not settings.DEBUG and not force:
            logger.info(f"Found overlay {style} at {path}")
            return True

        urls = style.split(",")
        logger.info(f"Embedding {len(urls)} overlay image(s) onto {path}")
        await asyncio.to_thread(shutil.copy, image, path)

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
        if url.strip() in {"", "default"}:
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
            # TODO: Can 'merge' and 'embed' be combined?
            if background.suffix == ".gif":
                await asyncio.to_thread(
                    utils.images.merge, self, index, Path(foreground), Path(background)
                )
            else:
                await asyncio.to_thread(
                    utils.images.embed, self, index, Path(foreground), Path(background)
                )
        except utils.images.EXCEPTIONS as e:
            logger.error(e)
            await foreground.unlink(missing_ok=True)

        return await foreground.exists()

    def animate(self, start: str = "0.2,0.6", stop: str = "1.0,1.0"):
        try:
            starts = [float(value) for value in start.split(",") if value]
            stops = [float(value) for value in stop.split(",") if value]
        except ValueError:
            logger.error(f"Invalid text animation: {start=} {stop=}")
            return

        with frozen():
            with suppress(IndexError):
                for index, value in enumerate(starts):
                    self.text[index].start = value
            with suppress(IndexError):
                for index, value in enumerate(stops):
                    self.text[index].stop = value

        if starts or stops:
            logger.info(f"Updated {self} with: {starts=} {stops=}")

    def customize(self, *, center: str, scale: str | float):
        with frozen(self):
            if center:
                try:
                    xy = [float(value) for value in center.split(",")]
                except ValueError:
                    logger.error(f"Invalid overlay: {center=}")
                else:
                    self.overlay[0].center_x, self.overlay[0].center_y = xy
            if scale:
                try:
                    scale = float(scale)
                except ValueError:
                    logger.error(f"Invalid overlay: {scale=}")
                else:
                    self.overlay[0].scale = scale

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
