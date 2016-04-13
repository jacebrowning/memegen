#!env/bin/python
# pylint: disable=no-member

import logging

from memegen.settings import ProdConfig
from memegen.app import create_app
from memegen.domain import Text


def main():
    logging.info("Generating sample images...")

    app = create_app(ProdConfig)

    with app.app_context():

        for template in app.template_service.all():
            app.image_service.create(template, Text("_"))
            app.image_service.create(template, Text("_/_"))
            app.image_service.create(template, template.sample_text)


if __name__ == '__main__':
    main()
