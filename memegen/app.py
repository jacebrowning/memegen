import os
import logging
from urllib.parse import urlencode, unquote

from flask import request, current_app
from flask_api import FlaskAPI
from flask_api.exceptions import APIException, NotFound

from . import services
from . import stores
from . import routes
from . import extensions

log = logging.getLogger('api')


class TemplateNotFound(NotFound):
    detail = "Template not found."


class InvalidMaskedCode(NotFound):
    detail = "Masked URL does not match any image."


class FilenameTooLong(APIException):
    status_code = 414
    detail = "Filename too long."


def create_app(config):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    configure_logging(app)

    register_extensions(app)

    register_services(app)
    register_blueprints(app)

    return app


def configure_logging(app):
    if app.config['DEBUG']:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logging.getLogger('yorm').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def register_extensions(app):
    extensions.redis.init_app(app)


def register_services(app):
    exceptions = services.Exceptions(
        TemplateNotFound=TemplateNotFound,
        InvalidMaskedCode=InvalidMaskedCode,
        FilenameTooLong=FilenameTooLong,
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
        debug=app.config['DEBUG']
    )

    def log_request(response):
        if current_app.debug:
            path = request.path
            if request.args:
                path += "?%s" % unquote(urlencode(request.args))
            log.info("%s: %s - %i", request.method, path,
                     response.status_code)
        return response
    app.after_request(log_request)


def register_blueprints(app):
    app.register_blueprint(routes.static.blueprint)
    app.register_blueprint(routes.root.blueprint)
    app.register_blueprint(routes.templates.blueprint)
    app.register_blueprint(routes.links.blueprint)
    app.register_blueprint(routes.image.blueprint)
    app.register_blueprint(routes.overview.blueprint)
    app.register_blueprint(routes.generator.blueprint)
    app.register_blueprint(routes.latest.blueprint)
    app.register_blueprint(routes.aliases.blueprint)
