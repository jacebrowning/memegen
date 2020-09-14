import time
from urllib.parse import quote

import requests

SITE = "http://localhost:5000"


timestamp = int(time.time())
for index in range(999):
    x = timestamp + index

    background = f"https://api.memegen.link/images/fry.png?height=1000&x={x}"
    url = (
        f"{SITE}/images/custom/test-{x}.png?height=1000&background={quote(background)}"
    )
    response = requests.get(url)
    response.raise_for_status()

    response2 = requests.get(f"{SITE}/templates")
    response2.raise_for_status()
    data = response2.json()

    print(
        f"{index + 1:04d}: {response.elapsed} elapsed fetching image, "
        f"{response2.elapsed} elapsed fetching templates"
    )
