from typing import Iterable

COLUMNS_STYLE = """
<style>
#images {
   /* Prevent vertical gaps */
   line-height: 0;

   -webkit-column-count: 6;
   -webkit-column-gap:   0px;
   -moz-column-count:    6;
   -moz-column-gap:      0px;
   column-count:         6;
   column-gap:           0px;
}

#images img {
  /* Just in case there are inline attributes */
  width: 100% !important;
  height: auto !important;
}

@media (max-width: 1400px) {
  #images {
  -moz-column-count:    5;
  -webkit-column-count: 5;
  column-count:         5;
  }
}
@media (max-width: 1200px) {
  #images {
  -moz-column-count:    4;
  -webkit-column-count: 4;
  column-count:         4;
  }
}
@media (max-width: 1000px) {
  #images {
  -moz-column-count:    3;
  -webkit-column-count: 3;
  column-count:         3;
  }
}

body {
  margin: 0;
  padding: 0;
}
</style>
""".strip()

REFRESH_SCRIPT = r"""
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
"""

RESIZE_SCRIPT = """
<script
    src="https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.2.11/iframeResizer.contentWindow.js"
    integrity="sha512-RMBWitJB1ymY4l6xeYsFwoEgVCAnOWX/zL1gNwXjlUj78nZ8SVbJsZxbH/w0p2jDNraHkOW8rzQgcJ0LNSXWBA=="
    crossorigin="anonymous">
</script>
"""

HTML = """
<!doctype html>
<html>
<head>
{head}
</head>
<body>
{body}
</body>
</html>
"""


def gallery(
    urls: Iterable[str],
    *,
    columns: bool,
    refresh: bool,
    rate: float = 3.0,
) -> str:
    if columns:
        return _columns_refresh(urls, rate) if refresh else _columns(urls)
    assert refresh
    return _grid_refresh(urls, rate)


def _columns(urls: Iterable[str]) -> str:
    elements = []

    for url in urls:
        elements.append(
            f"""
            <a href="https://memecomplete.com/edit/{url}" target="_blank">
                <img src="{url}?width=300">
            </a>
            """
        )

    elements.append(RESIZE_SCRIPT)

    images = "\n".join(elements).replace("\n" + " " * 12, "\n")

    head = "<title>memegen.link | examples</title>\n" + COLUMNS_STYLE
    body = f'<section id="images">\n{images}\n</section>'

    return HTML.format(head=head, body=body)


def _columns_refresh(urls: Iterable[str], rate: float) -> str:
    elements = []

    for url in urls:
        elements.append(
            f"""
            <a href="{url}">
                <img src="{url}?width=300&time=0">
            </a>
            """
        )

    elements.append(REFRESH_SCRIPT.replace("{interval}", str(int(rate * 3000))))

    images = "\n".join(elements).replace("\n" + " " * 12, "\n")

    head = "<title>memegen.link | debug</title>\n" + COLUMNS_STYLE
    body = f'<section id="images">\n{images}\n</section>'

    return HTML.format(head=head, body=body)


def _grid_refresh(urls: Iterable[str], rate: float):
    elements = []

    for url in urls:
        elements.append(
            f"""
            <a href="{url}">
                <img src="{url}?time=0">
            </a>
            """
        )

    elements.append(REFRESH_SCRIPT.replace("{interval}", str(int(rate * 3000))))

    images = "\n".join(elements).replace("\n" + " " * 12, "\n")

    head = "<title>memegen.link | test</title>\n"
    body = images

    return HTML.format(head=head, body=body)
