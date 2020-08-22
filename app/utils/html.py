from typing import Iterable


def gallery(urls: Iterable[str], *, refresh: bool = False, rate: float = 3.0) -> str:
    lines = []

    for url in urls:
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
                }, {interval});
            </script>
            """.replace(
                "{interval}", str(int(rate * 1000))
            )
        )

    return "\n".join(lines).replace("\n" + " " * 12, "\n")
