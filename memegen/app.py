import os

from flask_api import FlaskAPI, exceptions as api_exceptions

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
    exceptions = services.Exceptions(
        not_found=api_exceptions.NotFound,
        bad_code=api_exceptions.NotFound,
    )

    templates_root = os.path.join(app.config['ROOT'], 'data', 'templates')
    template_store = stores.template.TemplateStore(templates_root)
    images_root = os.path.join(app.config['ROOT'], 'data', 'images')
    image_store = stores.image.ImageStore(images_root)

    app.link_service = services.link.LinkService(
        exceptions=exceptions,
        template_store=template_store,
    )
    app.template_service = services.template.TemplateService(
        exceptions=exceptions,
        template_store=template_store,
    )
    app.image_service = services.image.ImageService(
        exceptions=exceptions,
        template_store=template_store,
        image_store=image_store,
    )


def register_blueprints(app):
    app.register_blueprint(routes.root.blueprint)
    app.register_blueprint(routes.templates.blueprint)
    app.register_blueprint(routes.links.blueprint)
    app.register_blueprint(routes.image.blueprint)
    app.register_blueprint(routes.overview.blueprint)
