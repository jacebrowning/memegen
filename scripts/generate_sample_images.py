import os
import sys
import time
import logging

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT)

from memegen.settings import ProdConfig
from memegen.app import create_app


def run(loop=True):
    logging.info("generating sample images...")

    app = create_app(ProdConfig)

    for template in app.template_service.all():
        app.image_service.create_image(template, template.sample_text)


if __name__ == '__main__':
    run()
