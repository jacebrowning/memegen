from urllib.parse import quote

import requests

SITE = "http://localhost:5000"


for index in range(999):
    background = f"https://api.memegen.link/images/fry.png?height=1000&index={index}"
    url = f"{SITE}/images/custom/test-{index}.png?background={quote(background)}"
    response = requests.get(url)
    print(response)
