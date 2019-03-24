import random
from pathlib import Path

from flask import (Blueprint, Markup,
                   render_template, current_app, make_response)
from markdown import markdown

from ._utils import samples


blueprint = Blueprint('index-page', __name__)


@blueprint.route("/")
def get():
    template_images = list(samples(blank=True))
    html = render_template(
        "index.html",
        template_images=template_images,
        default_template=random.choice(template_images)['key'],
        readme=_load_readme(),
        config=current_app.config,
    )
    response = make_response(html)
    response.headers['Cache-Control'] = f'max-age={60*60*12}'
    return response


def _load_readme():
    path = Path(current_app.config['ROOT'], 'README.md')
    with path.open() as f:
        text = f.read()
        content = text.split('<!--content-->')[-1]
        html = markdown(content, extensions=[
            'markdown.extensions.tables',
            'pymdownx.magiclink',
        ])
        return Markup(html)
