from typing import Iterable, Tuple


def gallery(samples: Iterable[Tuple[str, str]], *, refresh: bool = False) -> str:
    lines = []

    for url, template in samples:
        if refresh:
            url += "?time=0"
        else:
            url += "?width=300&height=300"
        lines.append(
            f"""
            <a href="{url}">
                <img src="{url}" style="padding: 5px; max-width: 600px; max-height: 600px">
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
