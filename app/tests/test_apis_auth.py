def describe_root():
    def describe_GET():
        def it_returns_401_when_unauthenticated(expect, client):
            request, response = client.get("/auth")
            expect(response.status) == 401
            expect(response.json) == {"message": "Your API key is invalid."}
