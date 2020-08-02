from pathlib import Path
from typing import List, Optional

from . import images
from .models import Template


def save_image(key: str, lines: str = "_", *, path: Optional[Path] = None) -> Path:
    template = Template.objects.get_or_none(key) or Template.objects.get("_error")
    path = images.save(template, lines, path=path)
    return path


def display_images(urls: List[str], *, refresh: bool = False) -> str:
    lines = []

    for url in urls:
        if refresh:
            url += "?time=0"
        lines.append(
            f"""
            <a href="{url}">
                <img src="{url}" width="500" style="padding: 5px;">
            </a>
            """
        )

    if refresh:
        lines.append(
            r"""
            <script>
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
        )

    return "\n".join(lines).replace("\n" + " " * 12, "\n")
