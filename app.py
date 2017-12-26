from apistar import Include, Route, typesystem, reverse_url
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls


class Font(typesystem.String):
    pass

class Style(typesystem.String):
    pass


class Dimension(typesystem.Integer):
    minimum = 50


class Meme(typesystem.Object):
    properties = {
        'top': typesystem.string(),
        'bottom': typesystem.string(),

        'font': typesystem.string(),
        'style': typesystem.string(),

        'width': Dimension,
        'height': Dimension,
    }


def list_templates():
    return []


def list_fonts():
    return []


def create_meme(name, meme: Meme):
    return {
        'image_url': reverse_url('get_image',
            template=name,
            top=meme.properties['top'],
            bottom=meme.properties['bottom'],
        ),
    }


def get_image(template, top, bottom, font: Font, style: Style, width: Dimension, height: Dimension):
    return f"{top} / {bottom}"





routes = [
    Route('/templates/', 'GET', list_templates),
    Route('/fonts/', 'GET', list_fonts),
    Route('/templates/{name}', 'POST', create_meme),
    Route('/images/{template}/{top}/{bottom}.jpg', 'GET', get_image),

    Include('/docs', docs_urls),
    Include('/static', static_urls)
]

app = App(routes=routes)
