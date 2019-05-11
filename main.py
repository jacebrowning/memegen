from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from sanic import Sanic, response

from datafiles import datafile
from models import Template

app = Sanic()


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
    text: List[Text] = field(default_factory=lambda: [Text(), Text()])

    def render(self, *lines) -> Path:
        return Path("templates", self.key, "default.jpg")


custom = Template("_custom")
error = Template("_error")


@app.route("/<key>/<line_0>.jpg")
async def image_lines_1(request, key, line_0):
    template = Template.datafiles.get_or_none(key) or error
    path = template.render(line_0)
    return await response.file(path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
