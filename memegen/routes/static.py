from flask import Blueprint


blueprint = Blueprint('static', __name__, url_prefix="/",
                      static_folder="../static")


@blueprint.route("stylesheets/<filename>")
def get_css(filename):
    return blueprint.send_static_file("stylesheets/{}".format(filename))


@blueprint.route("images/<filename>")
def get_image(filename):
    return blueprint.send_static_file("images/{}".format(filename))
