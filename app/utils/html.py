from typing import Iterable

STYLE = """
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


def gallery(urls: Iterable[str], *, refresh: bool = False, rate: float = 3.0) -> str:
    elements = []

    for href in urls:
        src = href + ("?time=0" if refresh else "?height=300")
        size = "" if refresh else 'width="300" height="300"'
        elements.append(
            f"""
            <a href="{href}">
                <img src="{src}" {size}>
            </a>
            """
        )

    if refresh:
        elements.append(REFRESH_SCRIPT.replace("{interval}", str(int(rate * 3000))))
    else:
        elements.append(RESIZE_SCRIPT)

    images = "\n".join(elements).replace("\n" + " " * 12, "\n")

    head = "<title>memegen.link</title>\n" + STYLE
    body = f'<section id="images">\n{images}\n</section>'

    return HTML.format(head=head, body=body)
