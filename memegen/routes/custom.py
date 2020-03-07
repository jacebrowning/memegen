from quart import Blueprint, render_template, current_app, make_response
from webargs import fields, flaskparser

from . image import PLACEHOLDER


OPTIONS = {
    'font': fields.Str(missing='titilliumweb-black'),
    'image': fields.URL(missing=PLACEHOLDER),
}


blueprint = Blueprint('custom-page', __name__)


@blueprint.route("/custom")
@flaskparser.use_kwargs(OPTIONS)
async def get(font, image):
    html = await render_template(
        'custom.html',
        fonts=sorted(current_app.font_service.all()),
        font=font,
        image=image,
        config=current_app.config,
    )
    response = await make_response(html)
    response.headers['Cache-Control'] = f'max-age={60*60*24*7}'
    return response
