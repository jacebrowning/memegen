import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from sanic import Sanic, response
from sanic.exceptions import abort
from sanic_openapi import swagger_blueprint

from datafiles import converters, datafile

app = Sanic(strict_slashes=True)
app.blueprint(swagger_blueprint)
app.config.SERVER_NAME = os.getenv("DOMAIN", "localhost:8000")


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

    @property
    def data(self) -> Dict:
        return {
            "name": self.name,
            "styles": [s for s in self.styles if s != "default"],
            "blank": app.url_for("image_blank", key=self.key, _external=True),
            "sample": app.url_for(
                "image_text", key=self.key, lines="/".join(self.sample), _external=True
            ),
            "source": self.source,
            "_self": app.url_for("templates_detail", key=self.key, _external=True),
        }

    def render(self, *lines) -> Path:
        print(f"TODO: render lines: {lines}")
        return self._get_background_image_path()

    def _get_background_image_path(self, name="default") -> Path:
        for ext in ["png", "jpg"]:
            path = Path("templates", self.key, f"default.{ext}")
            if path.exists():
                return path
        raise ValueError(f"No background image for template: {self}")


custom = Template("_custom")
error = Template("_error")


@app.get("/")
async def index(request):
    return response.json(
        {
            "templates": app.url_for("templates", _external=True),
            "images": app.url_for("images", _external=True),
            "_docs": app.url_for("swagger.index", _external=True),
        }
    )


@app.get("/templates")
async def templates(request):
    templates = Template.objects.filter(valid=True)
    return response.json([t.data for t in templates])


@app.get("/templates/<key>")
async def templates_detail(request, key):
    template = Template.objects.get_or_none(key)
    if template:
        return response.json(template.data)
    abort(404)


@app.get("/images")
async def images(request):
    templates = Template.objects.filter(valid=True)
    return response.json([])  # TODO: return sample images


@app.get("/images/<key>.jpg")
async def image_blank(request, key):
    template = Template.objects.get_or_none(key) or error
    path = template.render("_")
    return await response.file(path)


@app.get("/images/<key>/<lines:path>.jpg")
async def image_text(request, key, lines):
    template = Template.objects.get_or_none(key) or error
    path = template.render(lines.split("/"))
    return await response.file(path)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=int(os.environ.get("WEB_CONCURRENCY", 1)),
        debug=bool(os.environ.get("DEBUG", False)),
    )
