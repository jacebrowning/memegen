from random import randint
from urllib.parse import quote

from locust import HttpUser, between, task


class Client(HttpUser):

    host = "http://localhost:5000"

    wait_time = between(1, 2)

    @task
    def index(self):
        self.client.get("/")

    @task
    def docs(self):
        self.client.get("/docs")

    @task
    def samples(self):
        self.client.get("/samples")

    @task
    def templates(self):
        self.client.get("/templates")

    @task
    def image(self):
        x = randint(1000000, 9999999)
        background = quote(f"https://i.imgur.com/1TnC5pM.jpg?x={x}")
        path = f"/images/custom/test-{x}.png?height=1000&background={background}"
        self.client.get(path)
