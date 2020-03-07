from quart import Blueprint


blueprint = Blueprint('static', __name__, static_folder="../static")


@blueprint.route("/stylesheets/<filename>")
async def get_css(filename):
    return blueprint.send_static_file("stylesheets/{}".format(filename))


@blueprint.route("/images/<filename>")
async def get_image(filename):
    return blueprint.send_static_file("images/{}".format(filename))
