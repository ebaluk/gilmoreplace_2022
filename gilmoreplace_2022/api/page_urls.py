"""Build public page paths for the headless API without relying on wagtail_serve."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from wagtail.models import Site

if TYPE_CHECKING:
    from django.http import HttpRequest
    from wagtail.models import Page


def page_public_path(page: "Page", request: Optional["HttpRequest"] = None) -> str:
    """
    Relative public URL path for a Wagtail page (e.g. ``/en/homes/``).

    Uses site root ``url_path`` so headless setups do not need ``wagtail_serve``
    registered for ``Page.get_url()`` / ``page.url`` to work in API payloads.
    """
    if page is None:
        return "/"

    site = None
    if request is not None:
        site = Site.find_for_request(request)
    if site is None:
        site = Site.objects.filter(is_default_site=True).first()

    page_path = getattr(page, "url_path", None) or "/"
    if not site:
        return page_path if page_path.startswith("/") else f"/{page_path}"

    root_path = site.root_page.url_path or "/"
    if page_path.startswith(root_path):
        relative = page_path[len(root_path) :]
    else:
        relative = page_path.lstrip("/")

    if not relative:
        return "/"
    return relative if relative.startswith("/") else f"/{relative}"
