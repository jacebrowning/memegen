from flask_api import FlaskAPI, exceptions

from . import services
from . import stores
from . import routes


def create_app(config):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    register_services(app)
    register_blueprints(app)

    return app


def register_services(app):
    _exceptions = services.Exceptions(
        not_found=exceptions.NotFound,
        bad_code=exceptions.NotFound,
    )

    _template_store = stores.template.TemplateStore()
    _image_store = stores.image.ImageStore()

    app.link_service = services.link.LinkService(
        exceptions=_exceptions,
        template_store=_template_store,
    )
    app.template_servcie = services.template.TemplateService(
        exceptions=_exceptions,
        template_store=_template_store,
    )
    app.image_service = services.image.ImageService(
        exceptions=_exceptions,
        template_store=_template_store,
        image_store=_image_store,
    )


def register_blueprints(app):
    app.register_blueprint(routes.link.blueprint)
    app.register_blueprint(routes.image.blueprint)
