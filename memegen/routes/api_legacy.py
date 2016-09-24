from flask import Blueprint, current_app as app, redirect

from ._utils import route


blueprint = Blueprint('legacy', __name__)


@blueprint.route("/templates/")
def legacy_templates_index():
    return redirect(route('templates.get'))


@blueprint.route("/<key>")
def legacy_templates_detail(key):
    template = app.template_service.find(key)
    return redirect(route('templates.create', key=template.key))


@blueprint.route("/<key>/<path:path>")
def legacy_links_detail(**kwargs):
    return redirect(route('links.get', **kwargs))


@blueprint.route("/_<code>")
def legacy_links_detail_encoded(code):
    key, path = app.link_service.decode(code)
    return redirect(route('links.get', key=key, path=path))
