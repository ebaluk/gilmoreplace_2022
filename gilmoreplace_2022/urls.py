from django.urls import include, re_path
from django.conf import settings
from django.http import HttpResponseRedirect

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from wtadmin import urls as wtadmin_urls
from wtsitemap import urls as wtsitemap_urls

from .views import pdf_document_serve
from interactivemaps import urls as interactivemaps_urls

from .api_router import api_router, headless_urls_patterns

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# api_router.urls returns a 3-tuple (patterns, app_name, namespace)
api_patterns, api_app_name, api_namespace = api_router.urls


def _nextjs_base():
    return (
        getattr(settings, "NEXTJS_PUBLIC_URL", None)
        or getattr(settings, "NEXTJS_BASE_URL", "http://localhost:3000")
    ).rstrip("/")


def redirect_to_nextjs(request, path=""):
    """Send leftover public page hits to the Next.js frontend."""
    target = f"{_nextjs_base()}/{path.lstrip('/')}"
    if request.META.get("QUERY_STRING"):
        target = f"{target}?{request.META['QUERY_STRING']}"
    return HttpResponseRedirect(target)


def wagtail_serve_redirect(request, path):
    """
    Named ``wagtail_serve`` so Page.get_url() / reverse() keep working headless.
    Actual page HTML is served by Next.js.
    """
    return redirect_to_nextjs(request, path)


urlpatterns = (
    wtadmin_urls.urlpatterns
    + wtsitemap_urls.urlpatterns
    + interactivemaps_urls.urlpatterns
    + [
        re_path(r'^admin/', include(wagtailadmin_urls)),
        re_path(r'^documents/(\d+)/(.*\.pdf)$', pdf_document_serve, name='pdf_document_serve'),
        re_path(r'^documents/(\d+)/(.*\.PDF)$', pdf_document_serve, name='pdf_document_serve'),
        re_path(r'^documents/', include(wagtaildocs_urls)),
        re_path(r'^api/v2/', include((api_patterns, api_app_name), namespace=api_namespace)),
        re_path(r'^api/schema/$', SpectacularAPIView.as_view(), name='api_schema'),
        re_path(
            r'^api/docs/$',
            SpectacularSwaggerView.as_view(url_name='api_schema'),
            name='api_docs',
        ),
    ]
    + headless_urls_patterns
)

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Must be named wagtail_serve — Wagtail Page.get_url() reverses this route.
# Pattern matches wagtail.urls serve_pattern.
urlpatterns += [
    re_path(r"^((?:[\w\-]+/)*)$", wagtail_serve_redirect, name="wagtail_serve"),
    re_path(r"^(?P<path>.*)$", redirect_to_nextjs),
]
