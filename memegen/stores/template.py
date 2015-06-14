import os


class TemplateStore:

    def read(self, template):
        template.path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'templates', 'iw.png')
        return template
