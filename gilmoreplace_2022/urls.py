from django.urls import include, re_path
from django.conf import settings

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

from wtforms.views import WtFormView

from wtadmin import urls as wtadmin_urls
from wtsitemap import urls as wtsitemap_urls

from wt404test import urls as wt404test_urls

from .views import pdf_document_serve
from interactivemaps import urls as interactivemaps_urls

from .api_router import api_router, headless_urls_patterns

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# api_router.urls returns a 3-tuple (patterns, app_name, namespace)
api_patterns, api_app_name, api_namespace = api_router.urls

urlpatterns = (
    wtadmin_urls.urlpatterns
    + wtsitemap_urls.urlpatterns
    + interactivemaps_urls.urlpatterns
    + wt404test_urls.urlpatterns
    + [
        re_path(r'^admin/', include(wagtailadmin_urls)),
        re_path(r'^wtform/(?P<pk>\d+)/$', WtFormView.as_view()),
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
    + [
        re_path(r'', include(wagtail_urls)),
    ]
)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
