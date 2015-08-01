from flask import Blueprint


blueprint = Blueprint('static', __name__, url_prefix="/",
                      static_folder='../static')


@blueprint.route("stylesheets/<name>.css")
def get_css(name):
    return blueprint.send_static_file("stylesheets/{}.css".format(name))
