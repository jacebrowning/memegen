from flask import Blueprint, current_app as app, redirect

from ..domain import Text

from ._common import route


blueprint = Blueprint('magic', __name__)


@blueprint.route("/magic/")
def get():
    """Get a list of all matching links."""
    return []


@blueprint.route("/magic/<pattern>")
def links(pattern):
    """Get a list of all matching links."""
    text = Text(pattern)
    if text.path != pattern:
        return redirect(route('.links', pattern=text.path))

    return _get_matches(str(text))


def _get_matches(pattern):
    items = []

    for template in app.template_service.all():
        ratio, path = template.match(pattern)
        if not ratio:
            continue

        data = {}
        data['ratio'] = ratio
        data['template'] = route('links.get', key=template.key,
                                 path=path, _external=True)

        items.append(data)

    return sorted(items, key=lambda item: item['ratio'])


@blueprint.route("/m/<pattern>")
def links_shortened(pattern):
    """Redirect to the full magic route."""
    return redirect(route('.links', pattern=pattern))


@blueprint.route("/magic/<pattern>.jpg")
def image(pattern):
    """Get the first matching image."""
    items = []

    for template in app.template_service.all():
        ratio, path = template.match(pattern)
        if not ratio:
            continue

        data = {}
        data['ratio'] = ratio
        data['image'] = route('image.get', key=template.key, path=path)

        items.append(data)

    try:
        url = max(items, key=lambda item: item['ratio'])['image']
    except ValueError:
        url = route('image.get', key="unknown", path="_")

    return redirect(url)
