#!env/bin/python
# pylint: disable=no-member

import logging

from memegen.settings import ProdConfig
from memegen.app import create_app


def main():
    logging.info("Generating sample images...")

    app = create_app(ProdConfig)

    for template in app.template_service.all():
        app.image_service.create(template, template.sample_text)


if __name__ == '__main__':
    main()
