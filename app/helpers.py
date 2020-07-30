from pathlib import Path
from typing import List, Optional

from . import images
from .models import Template

RELOAD_IMAGES_SCRIPT = r"""<script>
setInterval(function() {
    var images = document.images;
    for (var i=0; i<images.length; i++) {
        images[i].src = images[i].src.replace(
            /\btime=[^&]*/, 'time=' + new Date().getTime()
        );
    }
}, 2000);
</script>
"""


def save_image(key: str, lines: str = "_", *, path: Optional[Path] = None) -> Path:
    template = Template.objects.get_or_none(key) or Template.objects.get("_error")
    path = images.save(template, lines, path=path)
    return path


def display_images(urls: List[str], *, debug: bool = False) -> str:
    html = f'<meta http-equiv="refresh" content="60">\n' if debug else ""

    for url in urls:
        if debug:
            url += "?time=0"
        html += f'<img src="{url}" width="500" style="padding: 5px;">\n'

    if debug:
        html += RELOAD_IMAGES_SCRIPT

    return html
