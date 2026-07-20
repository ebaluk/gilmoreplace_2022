"""Page detail response schema (stream_field kept flexible)."""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field

from .common import ApiModel, ImageData


class StreamFieldBlock(ApiModel):
    """One StreamField block; ``value`` shape varies by ``type``."""

    model_config = ConfigDict(extra="allow")

    type: str
    value: Any = None
    id: str | None = None


class PageRef(ApiModel):
    id: int
    title: str = ""
    slug: str | None = None
    url: str | None = None


class PageMetaBlock(ApiModel):
    site_name: str | None = None
    title: str | None = None
    description: str | None = None
    og_image: ImageData | None = None
    fb_app_id: str | None = None
    keywords: str | None = None


class PageResponse(ApiModel):
    """GET /api/v2/headless/pages/<id>/ and by-slug."""

    model_config = ConfigDict(extra="allow")

    id: int
    title: str
    slug: str = ""
    content_type: str = "page"
    url: str | None = None
    seo_title: str = ""
    search_description: str = ""
    show_in_menus: bool = False
    theme: Any = None
    color_theme: str = "default"
    show_navbar: bool = False
    show_in_sitemap: bool = True
    redirect_to_first_child: bool = False
    content_page_id: int | None = None
    hero: dict[str, Any] = Field(default_factory=dict)
    stream_field: list[Any] = Field(default_factory=list)
    meta: PageMetaBlock | dict[str, Any] | None = None
    language_code: str | None = None
    parent: PageRef | dict[str, Any] | None = None
    children: list[Any] = Field(default_factory=list)
    promo_box: Any = None
