from collections import OrderedDict

from flask import Blueprint, url_for, current_app, render_template, Response

from ._common import GITHUB_BASE, CONTRIBUTING


blueprint = Blueprint('root', __name__, url_prefix="/",
                      template_folder='../templates')


@blueprint.route("")
def get_index():
    tid = current_app.config['GOOGLE_ANALYTICS_TID']
    return Response(render_template("index.html", ga_tid=tid))


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    tid = current_app.config['GOOGLE_ANALYTICS_TID']
    return render_template("js/default.js", ga_tid=tid)


@blueprint.route("api")
def get():
    """Generate memes from templates."""
    data = OrderedDict()
    data['templates'] = url_for("templates.get", _external=True)
    data['overview'] = url_for("overview.get", _external=True)
    data['source'] = GITHUB_BASE
    data['contributing'] = CONTRIBUTING
    return data


@blueprint.route("CHECK")
def handle_checks():
    """Return CHECK_OK for zero-downtime deployment.

    See: https://labnotes.org/zero-downtime-deploy-with-dokku
    """
    return "CHECK_OK"
