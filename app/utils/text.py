import hashlib
import re
from urllib.parse import unquote


def encode(lines: list[str]) -> str:
    encoded_lines = []

    for line in lines:
        if line == "/":
            encoded_lines.append("_")
        elif line:
            encoded = unquote(line)
            for before, after in [
                ("_", "__"),
                ("-", "--"),
                (" ", "_"),
                ("?", "~q"),
                ("%", "~p"),
                ("#", "~h"),
                ('"', "''"),
                ("/", "~s"),
                ("\\", "~b"),
                ("\n", "~n"),
                ("&", "~a"),
                ("<", "~l"),
                (">", "~g"),
                ("‘", "'"),
                ("’", "'"),
                ("“", '"'),
                ("”", '"'),
                ("–", "-"),
            ]:
                encoded = encoded.replace(before, after)
            encoded_lines.append(encoded)
        else:
            encoded_lines.append("_")

    slug = "/".join(encoded_lines)

    return slug or "_"


def decode(slug: str) -> list[str]:
    has_dash = "_----" in slug
    has_arrow = "_--~g" in slug

    slug = slug.replace("_", " ").replace("  ", "_")
    slug = slug.replace("-", " ").replace("  ", "-")
    slug = slug.replace("''", '"')

    if has_dash:
        slug = slug.replace("-- ", " --")
    if has_arrow:
        slug = slug.replace("- ~g", " -~g")

    for before, after in [
        ("~q", "?"),
        ("~p", "%"),
        ("~h", "#"),
        ("~n", "\n"),
        ("~a", "&"),
        ("~l", "<"),
        ("~g", ">"),
        ("~b", "\\"),
    ]:
        slug = slug.replace(before, after)

    lines = slug.split("/")
    lines = [line.replace("~s", "/") for line in lines]

    return lines


def normalize(slug: str) -> tuple[str, bool]:
    slug = unquote(slug)
    normalized_slug = encode(decode(slug))
    return normalized_slug, slug != normalized_slug


def fingerprint(value: str, *, prefix="_custom-", suffix="") -> str:
    return prefix + hashlib.sha1(value.encode()).hexdigest() + suffix


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", value).strip("-")
