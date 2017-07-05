import os
import logging
from pathlib import Path
from urllib.parse import urlencode, unquote

from flask import request, current_app, url_for
from flask_api import FlaskAPI
from flask_api.exceptions import APIException, NotFound

from . import extensions
from . import services
from . import stores
from . import routes


log = logging.getLogger('api')


class TemplateNotFound(NotFound):
    detail = "Template not found."


class InvalidMaskedCode(NotFound):
    detail = "Masked URL does not match any image."


class FilenameTooLong(APIException):
    status_code = 414
    detail = "Filename too long."


class InvalidImageLink(APIException):
    status_code = 415
    detail = "Unsupported image type."


def create_app(config):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    configure_logging(app)

    register_extensions(app)
    register_services(app)
    register_blueprints(app)

    enable_cache_busting(app)

    return app


def configure_logging(app):
    logging.basicConfig(level=app.config['LOG_LEVEL'],
                        format="%(levelname)s: %(message)s")
    logging.getLogger('yorm').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.INFO)


def register_extensions(app):
    extensions.cors.init_app(app, methods=['GET', 'OPTIONS'], allow_headers='*')


def register_services(app):
    exceptions = services.Exceptions(
        TemplateNotFound,
        InvalidMaskedCode,
        FilenameTooLong,
        InvalidImageLink,
    )

    templates_root = os.path.join(app.config['ROOT'], 'data', 'templates')
    template_store = stores.template.TemplateStore(templates_root)

    fonts_root = os.path.join(app.config['ROOT'], 'data', 'fonts')
    font_store = stores.font.FontStore(fonts_root)

    images_root = os.path.join(app.config['ROOT'], 'data', 'images')
    image_store = stores.image.ImageStore(images_root, app.config)

    app.link_service = services.link.LinkService(
        exceptions=exceptions,
        template_store=template_store,
    )
    app.template_service = services.template.TemplateService(
        exceptions=exceptions,
        template_store=template_store,
    )
    app.font_service = services.font.FontService(
        exceptions=exceptions,
        font_store=font_store
    )
    app.image_service = services.image.ImageService(
        exceptions=exceptions,
        template_store=template_store,
        font_store=font_store,
        image_store=image_store,
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
    app.register_blueprint(routes.api_aliases.blueprint)
    app.register_blueprint(routes.api_fonts.blueprint)
    app.register_blueprint(routes.api_legacy.blueprint)
    app.register_blueprint(routes.api_links.blueprint)
    app.register_blueprint(routes.api_root.blueprint)
    app.register_blueprint(routes.api_search.blueprint)
    app.register_blueprint(routes.api_templates.blueprint)
    app.register_blueprint(routes.custom.blueprint)
    app.register_blueprint(routes.image.blueprint)
    app.register_blueprint(routes.index.blueprint)
    app.register_blueprint(routes.latest.blueprint)
    app.register_blueprint(routes.static.blueprint)


def enable_cache_busting(app):

    def dated_url_for(endpoint, **values):
        if endpoint == 'static':
            filename = values.get('filename', None)
            if filename:
                path = Path(app.root_path, endpoint, filename)
                values['q'] = int(path.stat().st_mtime)
        return url_for(endpoint, **values)

    app.context_processor(lambda: dict(url_for=dated_url_for))
