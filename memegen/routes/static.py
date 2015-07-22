from flask import Blueprint


blueprint = Blueprint('static', __name__, url_prefix="/",
                      static_folder='../static')


@blueprint.route("", endpoint='get')
def get_index():
    return blueprint.send_static_file("index.html")


@blueprint.route("stylesheets/<name>.css")
def get_css(name):
    return blueprint.send_static_file("stylesheets/{}.css".format(name))


@blueprint.route("flask-api/static/js/default.js")
def get_javascript():
    return blueprint.send_static_file("js/default.js")
