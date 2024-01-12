import asyncio
import shutil
from contextlib import suppress
from functools import cached_property
from pathlib import Path

from anyio import Path as AsyncPath
from datafiles import datafile, field, frozen
from furl import furl
from sanic import Request
from sanic.log import logger

from .. import settings, utils
from ..types import Dimensions
from .overlay import Overlay
from .text import Text


@datafile("../../templates/{self.id}/config{self.variant}.yml", defaults=True)
class Template:
    id: str
    variant: str = ""
    name: str = ""
    source: str | None = None
    keywords: list[str] = field(default_factory=list)

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
        return all(
            (
                not self.id.startswith("_"),
                "/" not in self.name,
                self.image.suffix != settings.PLACEHOLDER_SUFFIX,
            )
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

    @property
    def layout(self) -> str:
        if utils.urls.schema(self.source):
            return ""
        return self.source or ""

    @layout.setter
    def layout(self, value: str):
        if value not in {"", "default"}:
            self.source = value

    @layout.deleter
    def layout(self):
        if not utils.urls.schema(self.source):
            self.source = ""

    @cached_property
    def image(self) -> Path:
        return self.get_image()

    def get_image(self, style: str = "default", *, animated=False) -> Path:
        style = style or "default"
        style += "." + self.layout
        style = style.strip(".")
        level = 20 if (style != "default" or animated is True) else 10

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
            del self.layout

        return self.get_image()

    def jsonify(self, request: Request) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "lines": len(self.text),
            "overlays": len(self.overlay) if self.styles else 0,
            "styles": self.styles,
            "blank": request.app.url_for(
                "Images.detail_blank",
                template_filename=self.id + settings.DEFAULT_SUFFIX,
                _external=True,
                _scheme=settings.SCHEME,
            ),
            "example": {
                "text": self.example if any(self.example) else [],
                "url": self.build_example_url(request),
            },
            "source": self.source,
            "keywords": self.keywords,
            "_self": self.build_self_url(request),
        }

    def build_self_url(self, request: Request) -> str:
        return request.app.url_for(
            "Templates.detail",
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
        url = request.app.url_for("Images.detail_text", **kwargs)
        return utils.urls.clean(url)

    def build_custom_url(
        self,
        request: Request,
        text_lines: list[str],
        *,
        normalize: bool = True,
        extension: str = "",
        background: str = "",
        style: str = "",
        layout: str = "",
        font: str = "",
    ):
        if normalize:
            with suppress(IndexError):
                for index, text in enumerate(self.text):
                    text_lines[index] = text.normalize(text_lines[index])
        if not extension and background:
            url = furl(background)
            if url.path.segments:
                extension = url.path.segments[-1].split(".")[-1]
        if extension not in settings.ALLOWED_EXTENSIONS:
            extension = self._extension
        if style == "default":
            style = ""
        elif style == "animated":
            style = ""
            if extension not in settings.ANIMATED_EXTENSIONS:
                extension = settings.DEFAULT_ANIMATED_EXTENSION
        if layout == "default":
            layout = ""
        url = request.app.url_for(
            "Images.detail_text",
            template_id="custom" if self.id == "_custom" else self.id,
            text_filepath=utils.text.encode(text_lines) + "." + extension,
            _external=True,
            _scheme=settings.SCHEME,
            **utils.urls.params(
                background=background, style=style, layout=layout, font=font
            ),
        )
        return utils.urls.clean(url)

    @property
    def _extension(self) -> str:
        return (
            settings.DEFAULT_ANIMATED_EXTENSION
            if self.animated_image
            else settings.DEFAULT_STATIC_EXTENSION
        )

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
        identifier = str(self.text) + font_name + style + str(size) + watermark
        if self.overlay != [Overlay()]:
            identifier += str(self.overlay)
        if frames:
            identifier += str(frames)
        fingerprint = utils.text.fingerprint(identifier, prefix="")
        filename = f"{slug}.{fingerprint}.{extension}"
        return Path(self.id) / filename

    @classmethod
    async def create(cls, url: str, *, force=False) -> "Template":
        try:
            parsed = furl(url)
        except ValueError as e:
            logger.error(e)
            return cls.objects.get("_error")

        if utils.urls.self(parsed):
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
        template: Template = cls.objects.get_or_create(id, name=url)

        suffix = Path(str(parsed.path)).suffix
        if not suffix or len(suffix) > 10:
            logger.warning(f"Unable to determine image extension: {url}")
            suffix = settings.PLACEHOLDER_SUFFIX

        filename = "default" + suffix
        path = AsyncPath(template.directory) / filename

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
        path = AsyncPath(self.directory) / filename
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
        self, index: int, url: str, background: AsyncPath, force: bool
    ) -> bool:
        if url.strip() in {"", "default"}:
            return True

        suffix = Path(str(furl(url).path)).suffix
        if not suffix:
            logger.warning(f"Unable to determine image extension: {url}")
            suffix = ".png"

        filename = utils.text.fingerprint(url, prefix="_embed-", suffix=suffix)
        foreground = AsyncPath(self.directory) / filename

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

    async def clone(
        self, options: dict, lines: int = 1, style: str = "default", *, animated: bool
    ) -> "Template":
        layout = utils.urls.arg(options, "default", "layout")

        start = utils.urls.arg(options, "", "start")
        stop = utils.urls.arg(options, "", "stop")

        color = utils.urls.arg(options, None, "color")
        center = utils.urls.arg(options, None, "center")
        scale = utils.urls.arg(options, None, "scale")

        identifiers = [str(v) for v in (start, stop, color, center, scale) if v]
        if layout == "top":
            identifiers.extend([layout, str(lines)])
        variant = utils.text.fingerprint("|".join(identifiers), prefix=".")

        template: Template = self.objects.get_or_create(self.id, variant, self.name)
        template.animate(start, stop)
        template.customize(color, center, scale)
        await template.position(layout, lines, style, animated)

        return template

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

    def customize(self, color: str, center: str, scale: str | float):
        with frozen(self):
            if color:
                try:
                    colors = [value for value in color.split(",") if value]
                except ValueError:
                    logger.error(f"Invalid color: {color=}")
                else:
                    with suppress(IndexError):
                        for index, value in enumerate(colors):
                            self.text[index].color = value
            if center:
                try:
                    xy = [float(value) for value in center.split(",")]
                    self.overlay[0].center_x, self.overlay[0].center_y = xy
                except ValueError:
                    logger.error(f"Invalid overlay: {center=}")
            if scale:
                try:
                    scale = float(scale)
                except ValueError:
                    logger.error(f"Invalid overlay: {scale=}")
                else:
                    self.overlay[0].scale = scale

    async def position(self, layout: str, lines: int, style: str, animated: bool):
        if layout == "top":
            with frozen(self):
                self.overlay = self.overlay
                self.text = []
                for index in range(lines):
                    text = Text(
                        style="none",
                        color="black",
                        font="thin",
                        anchor_x=0.01,
                        anchor_y=index * 0.1,
                        scale_x=0.99,
                        scale_y=0.2 / lines,
                        align="left",
                    )
                    self.text.append(text)

            source = self.get_image(style=style, animated=animated)
            suffix = source.suffix
            if suffix == settings.PLACEHOLDER_SUFFIX:
                suffix = settings.DEFAULT_SUFFIX

            destination = Path(self.directory) / (source.stem + ".top" + suffix)
            await asyncio.to_thread(utils.images.pad_top, source, destination)
            self.layout = "top"

    def clean(self):
        for path in self.directory.iterdir():
            if path.stem not in {"config", "default"}:
                path.unlink()

    def delete(self):
        if self.directory.exists():
            shutil.rmtree(self.directory)

    def matches(self, query: str) -> bool:
        keywords = " ".join(line.lower() for line in self.keywords)
        example = " ".join(line.lower() for line in self.example)
        return any(
            (
                query in self.id,
                query in self.name.lower(),
                query in keywords,
                query in example,
            )
        )
