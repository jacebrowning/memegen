from typing import List


def encode(lines: List[str]) -> str:
    parts = []
    for line in lines:
        if line:
            encoded = (
                line.replace(" ", "_")
                .replace("?", "~q")
                .replace("%", "~p")
                .replace("#", "~h")
                .replace("/", "~s")
            )
            parts.append(encoded)
        else:
            parts.append("_")
    slug = "/".join(parts).lower()
    return slug


def decode(slug: str) -> List[str]:
    lines = (
        slug.replace("_", " ")
        .replace("-", " ")
        .replace("~q", "?")
        .replace("~p", "%")
        .replace("~h", "#")
        .split("/")
    )
    return [line.replace("~s", "/") for line in lines]
