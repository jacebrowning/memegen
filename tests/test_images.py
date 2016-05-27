# pylint: disable=bad-continuation

from pathlib import Path


SAMPLES = Path(__file__).parent.joinpath("samples")


def test_samples(client):
    """Create various sample images for manual verfification."""
    for name, url in [
        ("basic.jpg", "/ch/hello/world.jpg"),
        ("nominal.jpg", "/ch/a-normal-line-of-top-meme-text-followed-by/"
            "another-normal-line-of-bottom-meme-text.jpg"),
        ("long.jpg", "/ch/" + ("long-" * 15) + "line/short-line.jpg"),
        ("subscripts.jpg", "/ch/some-unicode-subscripts/h%E2%82%82o.jpg"),
    ]:
        with SAMPLES.joinpath(name).open('wb') as image:
            response = client.get(url)
            data = response.get_data()
            image.write(data)
