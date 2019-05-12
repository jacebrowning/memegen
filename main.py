from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from sanic import Sanic, response
from sanic.exceptions import abort

from datafiles import datafile
from models import Template

app = Sanic()

app.config.SERVER_NAME = "localhost:8000"


@dataclass
class Text:

    color: str = "white"

    anchor_x: float = 0.1
    anchor_y: float = 0.2

    angle: float = 0

    scale_x: float = 0.5
    scale_y: float = 0.6


@datafile("templates/{self.key}/config.yml")
class Template:

    key: str
    name: str = ""
    source_url: Optional[str] = None
    text: List[Text] = field(default_factory=lambda: [Text(), Text()])
    styles: List[str] = field(default_factory=lambda: ["default"])

    @property
    def data(self) -> Dict:
        return {
            "name": self.name,
            "base_url": app.url_for("templates_detail", key=self.key, _external=True),
            "icon_url": app.url_for(
                "image_lines_1",
                key=self.key,
                line_0="_",
                watermark="none",
                _external=True,
            ),
            "source_url": self.source_url,
            "text": self.text,
            "styles": self.styles,
        }

    def render(self, *lines) -> Path:
        print(f"TODO: render lines: {lines}")
        return self._get_background_image_path()

    def _get_background_image_path(self, name="default") -> Path:
        for ext in ["png", "jpg"]:
            path = Path("templates", self.key, f"default.{ext}")
            if path.exists():
                return path


custom = Template("_custom")
error = Template("_error")


@app.get("/")
async def index(request):
    return response.json({"templates": app.url_for("templates", _external=True)})


@app.get("/templates")
async def templates(request):
    keys = ["ds", "iw"]
    templates = [Template.datafiles.get_or_create(key) for key in keys]
    return response.json([t.data for t in templates])


@app.get("/templates/<key>")
async def templates_detail(request, key):
    template = Template.datafiles.get_or_none(key)
    if template:
        return response.json(template.data)
    abort(404)


@app.get("/images/<key>/<line_0>.jpg")
async def image_lines_1(request, key, line_0):
    template = Template.datafiles.get_or_none(key) or error
    path = template.render(line_0)
    return await response.file(path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
