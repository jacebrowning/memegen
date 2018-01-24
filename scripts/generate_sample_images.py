#!env/bin/python

import logging

from memegen.settings import ProdConfig
from memegen.factory import create_app
from memegen.domain import Text


def main():
    logging.info("Generating sample images...")

    app = create_app(ProdConfig)

    with app.app_context():

        for template in app.template_service.all():
            for text in [Text("_"), template.sample_text]:
                for watermark in ["", "memegen.link"]:
                    app.image_service.create(template, text,
                                             watermark=watermark)


if __name__ == '__main__':
    main()
