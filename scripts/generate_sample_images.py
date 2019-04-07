"""Prerender common images used in the application."""


from memegen.settings import ProductionConfig
from memegen.factory import create_app
from memegen.domain import Text


def run():
    app = create_app(ProductionConfig)
    with app.app_context():

        options = []
        for template in app.template_service.all():
            for text in [Text("_"), template.sample_text]:
                for watermark in ["", "memegen.link"]:
                    options.append((template, text, watermark))

        print(f"Generating {len(options)} sample images...")
        for template, text, watermark in options:
            app.image_service.create(template, text, watermark=watermark)


if __name__ == '__main__':
    run()
