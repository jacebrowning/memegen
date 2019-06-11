from server.main import app


def describe_templates():
    def describe_GET():
        def it_returns_all_templates(expect):
            request, response = app.test_client.get("/")
            expect(response.status) == 200
