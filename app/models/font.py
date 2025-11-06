from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from pathlib import Path

from sanic import Request

from .. import settings


class Manager:
    @staticmethod
    def get(name: str) -> Font:
        name = name or settings.DEFAULT_FONT
        for font in FONTS:
            if name in (font.id, font.alias):
                return font
        raise ValueError(f"Unknown font: {name}")

    @staticmethod
    def all() -> list[Font]:
        return FONTS


@dataclass
class Font:
    filename: str
    id: str
    _: KW_ONLY
    alias: str = ""

    objects = Manager()

    @property
    def path(self) -> Path:
        return settings.ROOT / "fonts" / self.filename

    def jsonify(self, request: Request) -> dict:
        return {
            "id": self.id,
            "alias": self.alias or None,
            "filename": self.filename,
            "_self": self.build_self_url(request),
        }

    def build_self_url(self, request: Request) -> str:
        return request.app.url_for(
            "Fonts.detail",
            id=self.id,
            _external=True,
            _scheme=settings.SCHEME,
        )


FONTS = [
    Font("TitilliumWeb-Black.ttf", "titilliumweb", alias="thick"),
    Font("NotoSans-Bold.ttf", "notosans"),
    Font("Kalam-Regular.ttf", "kalam", alias="comic"),
    Font("Impact.ttf", "impact"),
    Font("TitilliumWeb-SemiBold.ttf", "titilliumweb-thin", alias="thin"),
    Font("Segoe UI Bold.ttf", "segoe", alias="tiny"),
    Font("HG-Mincho-B.ttc", "hgminchob", alias="jp"),
    Font("NotoSansHebrew-Bold.ttf", "notosanshe", alias="he"),
]
