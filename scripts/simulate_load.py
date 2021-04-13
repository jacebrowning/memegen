"""
poetry run locust -f scripts/simulate_load.py
"""

from random import randint
from urllib.parse import quote

from locust import HttpUser, constant_pacing, task


class Client(HttpUser):

    host = "http://localhost:5000"
    wait_time = constant_pacing(10)

    @task(10)
    def image_from_template(self):
        x = randint(1000000, 9999999)
        path = f"/images/fry/test-{x}.jpg"
        self.client.get(path)

    @task(1)
    def image_from_template_large(self):
        x = randint(1000000, 9999999)
        path = f"/images/fry/test-{x}.png?height=1000"
        self.client.get(path)

    @task(3)
    def image_from_custom(self):
        x = randint(1000000, 9999999)
        background = quote(f"https://memegen.link/img/grid.png?x={x}")
        path = f"/images/custom/test-{x}.png?height=1000&background={background}"
        self.client.get(path)
