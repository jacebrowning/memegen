from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthResponse:
    email: str
    image_access: bool
    search_access: bool
    created: datetime
    modified: datetime


@dataclass
class FontResponse:
    filename: str
    id: str
    alias: str


@dataclass
class MemeRequest:
    template_id: str
    style: list[str]
    text_lines: list[str]
    font: str
    extension: str
    redirect: bool


@dataclass
class CustomRequest:
    background: str
    style: str
    text_lines: list[str]
    font: str
    extension: str
    redirect: bool


@dataclass
class AutomaticRequest:
    text: str
    safe: bool
    redirect: bool


@dataclass
class MemeResponse:
    url: str


@dataclass
class ExampleResponse:
    url: str
    template: str


@dataclass
class _Example:
    text: list[str]
    url: str


@dataclass
class TemplateResponse:
    id: str
    name: str
    lines: int
    overlays: int
    styles: list[str]
    blank: str
    example: _Example
    source: str
    _self: str


@dataclass
class ErrorResponse:
    error: str
