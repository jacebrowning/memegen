from typing import List


def encode_slug(lines: List[str]) -> str:
    parts = []
    for line in lines:
        if line:
            encoded = line.replace(" ", "_").replace("?", "~q")
            parts.append(encoded)
        else:
            parts.append("_")
    slug = "/".join(parts).lower()
    return slug


def decode_lines(slug: str) -> List[str]:
    lines = slug.replace("_", " ").replace("~q", "?").upper().split("/")
    return lines
