from flask import Blueprint, current_app as app, redirect

from ..domain import Text

from ._utils import route


blueprint = Blueprint('magic', __name__)


@blueprint.route("/magic/", defaults={'pattern': None}, endpoint='get')
@blueprint.route("/magic/<pattern>")
def links(pattern):
    """Get a list of all matching links."""
    if not pattern:
        return []

    text = Text(pattern)

    if text.path != pattern:
        return redirect(route('.links', pattern=text.path))

    return _get_matches(str(text).lower())


def _get_matches(pattern):
    items = []

    for template in app.template_service.all():
        ratio, path = template.match(pattern)
        if not ratio:
            continue

        data = {}
        data['ratio'] = ratio
        data['link'] = route('links.get', key=template.key,
                             path=path, _external=True)

        items.append(data)

    return sorted(items, key=lambda item: item['ratio'], reverse=True)


@blueprint.route("/m/<pattern>")
def links_shortened(pattern):
    """Redirect to the full magic route."""
    return redirect(route('.links', pattern=pattern))


@blueprint.route("/magic/<pattern>.jpg")
def image(pattern):
    """Get the first matching image."""
    # TODO: share this logic
    text = Text(pattern)

    items = []

    for template in app.template_service.all():
        ratio, path = template.match(str(text).lower())
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


@blueprint.route("/m/<pattern>.jpg")
def image_shortened(pattern):
    """Redirect to the first magic image."""
    return redirect(route('.image', pattern=pattern))
