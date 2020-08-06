from typing import Iterable


def gallery(urls: Iterable[str], *, refresh: bool = False) -> str:
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
