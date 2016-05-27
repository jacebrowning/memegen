# pylint: disable=bad-continuation

from pathlib import Path


SAMPLES = Path(__file__).parent.joinpath("samples")


def test_samples(client):
    """Create various sample images for manual verfification."""
    for name, url in [
        ("basic.jpg", "/iw/hello/world.jpg"),
        ("nominal.jpg", "/iw/a-normal-line-of-top-meme-text-followed-by/"
            "another-normal-line-of-bottom-meme-text.jpg"),
        ("long.jpg", "/iw/" + ("long-" * 15) + "line/short-line.jpg"),
        ("subscripts.jpg", "/iw/some-unicode-subscripts:/h%E2%82%82o.jpg"),
    ]:
        with SAMPLES.joinpath(name).open('wb') as image:
            response = client.get(url)
            data = response.get_data()
            image.write(data)
