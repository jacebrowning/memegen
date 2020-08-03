from typing import List


def encode(lines: List[str]) -> str:
    parts = []
    for line in lines:
        if line:
            encoded = line.replace(" ", "_").replace("?", "~q")
            parts.append(encoded)
        else:
            parts.append("_")
    return "/".join(parts).lower()


def decode(text: str) -> List[str]:
    return text.replace("_", " ").replace("~q", "?").upper().split("/")
