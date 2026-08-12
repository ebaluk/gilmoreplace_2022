from __future__ import absolute_import, unicode_literals

import requests

from django.conf import settings

from wagtail.signals import page_published, page_unpublished

from gilmoreplace_2022.api.page_urls import page_public_path


def revalidate_page(sender, instance, **kwargs):
    secret = getattr(settings, "REVALIDATION_SECRET", None)
    if not secret:
        return
    base_url = getattr(settings, "NEXTJS_BASE_URL", "http://localhost:3000")
    path = page_public_path(instance).rstrip("/") or "/"
    try:
        requests.post(
            f"{base_url.rstrip('/')}/api/revalidate",
            headers={"X-Revalidation-Secret": secret},
            json={
                "page_id": instance.id,
                "path": path,
                "slug": instance.slug,
            },
            timeout=5,
        )
    except requests.RequestException:
        pass


page_published.connect(revalidate_page)
page_unpublished.connect(revalidate_page)
