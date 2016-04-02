import random

from flask import Blueprint, Response, render_template

from ._common import GITHUB_SLUG, get_tid, samples


blueprint = Blueprint('index', __name__, url_prefix="/")


@blueprint.route("")
def get_index():
    imgs = list(samples())
    return Response(render_template(
        "index.html",
        imgs=imgs,
        default=random.choice(imgs)['key'],
        github_slug=GITHUB_SLUG,
        ga_tid=get_tid(),
    ))


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    return Response(render_template(
        "js/default.js",
        ga_tid=get_tid(),
    ))
