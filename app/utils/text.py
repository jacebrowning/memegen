from typing import List


def encode(lines: List[str]) -> str:
    encoded_lines = []

    for line in lines:
        if line:
            encoded = line.replace("_", "__").replace("-", "--")
            encoded = encoded.replace(" ", "_")
            encoded = encoded.replace("?", "~q").replace("%", "~p").replace("#", "~h")
            encoded = encoded.replace("/", "~s")
            encoded_lines.append(encoded)
        else:
            encoded_lines.append("_")

    slug = "/".join(encoded_lines).lower()

    return slug


def decode(slug: str) -> List[str]:
    slug = slug.replace("_", " ").replace("  ", "_")
    slug = slug.replace("-", " ").replace("  ", "-")

    slug = slug.replace("~q", "?").replace("~p", "%").replace("~h", "#")

    lines = slug.split("/")
    lines = [line.replace("~s", "/") for line in lines]

    return lines
