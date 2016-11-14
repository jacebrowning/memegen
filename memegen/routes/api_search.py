from collections import OrderedDict

from flask import Blueprint, current_app as app

from ._utils import route


blueprint = Blueprint('search', __name__, url_prefix="/api/search/")


@blueprint.route("<query>")
@blueprint.route("", defaults={'query': None})
def get(query):
    """Get a list of all matching links."""
    return _get_matches(query)


def _get_matches(query):
    items = []

    for template in app.template_service.all():
        count = template.search(query)

        if not count:
            continue

        data = OrderedDict()
        data['count'] = count
        data['template'] = OrderedDict()
        data['template']['name'] = template.name
        data['template']['description'] = template.link
        data['template']['blank'] = route('image.get', key=template.key,
                                          path='_', _external=True)
        data['template']['example'] = route('image.get', key=template.key,
                                            path=template.sample_path,
                                            _external=True)
        items.append(data)

    return sorted(items, key=lambda item: item['count'], reverse=True)
