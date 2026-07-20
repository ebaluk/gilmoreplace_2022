"""Shared Pydantic helpers and media shapes."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class ApiModel(BaseModel):
    """Base model: ignore unknown CMS fields so resolvers can grow safely."""

    model_config = ConfigDict(extra="ignore")


class ImageData(ApiModel):
    """Resolved Wagtail image rendition."""

    id: int
    title: str = ""
    width: int | None = None
    height: int | None = None
    url: str
    alt: str | None = None


def dump_model(model_cls: type[T], payload: Any) -> dict[str, Any]:
    """Validate ``payload`` with ``model_cls`` and return JSON-ready dict."""
    return model_cls.model_validate(payload).model_dump(mode="json")
