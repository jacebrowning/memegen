# pylint: disable=unused-variable,expression-not-assigned,singleton-comparison


from memegen import factory, settings


def describe_create_app():

    def when_dev(expect):
        app = factory.create_app(settings.LocalConfig)
        expect(app.config['DEBUG']) == True
        expect(app.config['TESTING']) == False

    def when_test(expect):
        app = factory.create_app(settings.TestConfig)
        expect(app.config['DEBUG']) == True
        expect(app.config['TESTING']) == True

    def when_prod(expect):
        app = factory.create_app(settings.ProductionConfig)
        expect(app.config['DEBUG']) == False
        expect(app.config['TESTING']) == False
