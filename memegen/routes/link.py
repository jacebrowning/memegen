from flask import Blueprint

blueprint = Blueprint('link', __name__, url_prefix="/")


@blueprint.route("<key>/<top>/<bottom>")
def get(key, top, bottom):
    return {}
