"""
poetry run locust -f scripts/simulate_load.py
"""

from random import randint
from urllib.parse import quote

from locust import HttpUser, between, task


class Client(HttpUser):

    host = "http://localhost:5000"

    wait_time = between(10, 60)

    @task(5)
    def index(self):
        self.client.get("/")

    @task(5)
    def docs(self):
        self.client.get("/docs")

    @task(1)
    def examples(self):
        self.client.get("/examples")

    @task(1)
    def templates(self):
        self.client.get("/templates")

    @task(100)
    def image_from_template(self):
        x = randint(1000000, 9999999)
        path = f"/images/fry/test-{x}.jpg"
        self.client.get(path)

    @task(10)
    def image_from_template_large(self):
        x = randint(1000000, 9999999)
        path = f"/images/fry/test-{x}.png?height=1000"
        self.client.get(path)

    @task(25)
    def image_from_custom(self):
        x = randint(1000000, 9999999)
        background = quote(f"https://memegen.link/img/grid.png?x={x}")
        path = f"/images/custom/test-{x}.png?height=1000&background={background}"
        self.client.get(path)
