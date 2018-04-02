#!env/bin/python

import log

from memegen.settings import ProductionConfig
from memegen.factory import create_app
from memegen.domain import Text


def main():
    log.info("Generating sample images...")

    app = create_app(ProductionConfig)

    with app.app_context():

        for template in app.template_service.all():
            for text in [Text("_"), template.sample_text]:
                for watermark in ["", "memegen.link"]:
                    app.image_service.create(template, text,
                                             watermark=watermark)


if __name__ == '__main__':
    main()
