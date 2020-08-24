from typing import List, Tuple


def encode(lines: List[str]) -> str:
    encoded_lines = []

    for line in lines:
        if line:
            encoded = line
            encoded = encoded.replace("_", "__").replace("-", "--")
            encoded = encoded.replace(" ", "_")
            encoded = encoded.replace("?", "~q").replace("%", "~p").replace("#", "~h")
            encoded = encoded.replace("/", "~s")
            encoded = encoded.replace("\n", "~n")
            encoded_lines.append(encoded)
        else:
            encoded_lines.append("_")

    slug = "/".join(encoded_lines)

    return slug or "_"


def decode(slug: str) -> List[str]:
    has_arrow = "_-->" in slug

    slug = slug.replace("_", " ").replace("  ", "_")
    slug = slug.replace("-", " ").replace("  ", "-")

    if has_arrow:
        slug = slug.replace("- >", " ->")

    slug = (
        slug.replace("~q", "?")
        .replace("~p", "%")
        .replace("~h", "#")
        .replace("~n", "\n")
    )

    lines = slug.split("/")
    lines = [line.replace("~s", "/") for line in lines]

    return lines


def normalize(slug: str) -> Tuple[str, bool]:
    normalized_slug = encode(decode(slug))
    return normalized_slug, slug != normalized_slug
