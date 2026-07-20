"""Headless preview helpers for Wagtail admin → Next.js ``/preview``."""

from urllib.parse import urlencode

from django.conf import settings
from wagtail_headless_preview.models import HeadlessPreviewMixin


class NextHeadlessPreviewMixin(HeadlessPreviewMixin):
    """Preview opens Next.js ``/preview?content_type=&token=`` (draft, not live path)."""

    def get_client_root_url(self, request):
        public = getattr(settings, "NEXTJS_PUBLIC_URL", None)
        if public:
            return public.rstrip("/")
        return super().get_client_root_url(request)

    def get_preview_url(self, request, token):
        root = self.get_client_root_url(request).rstrip("/")
        query = urlencode(
            {
                "content_type": self.get_content_type_str(),
                "token": token,
            }
        )
        return f"{root}/preview?{query}"
