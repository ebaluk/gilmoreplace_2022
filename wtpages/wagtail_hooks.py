from __future__ import absolute_import, unicode_literals

import requests

from django.conf import settings
from django.core.management import call_command

from wagtail import hooks
from wagtail.signals import page_published


def revalidate_page(sender, instance, **kwargs):
    secret = getattr(settings, "REVALIDATION_SECRET", None)
    if not secret:
        return
    base_url = getattr(settings, "NEXTJS_BASE_URL", "http://localhost:3000")
    try:
        requests.post(
            f"{base_url}/api/revalidate",
            json={
                "secret": secret,
                "page_id": instance.id,
                "slug": instance.slug,
            },
            timeout=5,
        )
    except requests.RequestException:
        pass


page_published.connect(revalidate_page)


@hooks.register("after_publish_page")
def after_publish_page_hook(request, page):
    revalidate_page(None, page)
