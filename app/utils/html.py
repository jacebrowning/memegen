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
@media (max-width: 800px) {
  #images {
  -moz-column-count:    2;
  -webkit-column-count: 2;
  column-count:         2;
  }
}
@media (max-width: 400px) {
  #images {
  -moz-column-count:    1;
  -webkit-column-count: 1;
  column-count:         1;
  }
}

body {
  margin: 0;
  padding: 0;
  background: black;
}
</style>
""".strip()

SCRIPT = r"""
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
        elements.append(SCRIPT.replace("{interval}", str(int(rate * 3000))))

    images = "\n".join(elements).replace("\n" + " " * 12, "\n")

    head = "<title>Samples</title>\n" + STYLE
    body = f'<section id="images">\n{images}\n</section>'

    return HTML.format(head=head, body=body)
