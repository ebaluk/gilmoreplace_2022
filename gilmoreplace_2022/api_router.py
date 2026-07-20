"""Wagtail + headless API routing for Gilmore Place.

Wagtail API v2 (via ``api_router``):
    /api/v2/pages/, /api/v2/images/, /api/v2/documents/

Custom headless API (``headless_urls``), used by Next.js:
    GET  /api/v2/headless/pages/                          AllPagesView
    GET  /api/v2/headless/pages/<id>/                     PageDetailView
    GET  /api/v2/headless/pages/by-slug/                  PageDetailView (slug+locale)
    GET  /api/v2/headless/pages/preview/                  PagePreviewView (draft token)
    GET  /api/v2/headless/navigation/                     NavigationView
    GET  /api/v2/headless/settings/                       SettingsView
    GET  /api/v2/headless/themes/                         ThemeView
    GET  /api/v2/headless/towers/                         TowerDataView
    GET  /api/v2/headless/maps/                           InteractiveMapsView
    GET  /api/v2/headless/google-maps/                    GoogleMapsInstancesView
    GET  /api/v2/headless/forms/<id>/                     FormDetailView
    POST /api/v2/headless/forms/<id>/submit/              FormSubmitView
    GET  /api/v2/headless/instagram/                      InstagramFeedView
    GET  /api/v2/headless/promobox/                       PromoBoxView
    POST /api/v2/headless/revalidate/                     RebuildWebhookView
    GET  /api/v2/headless/images/<id>/<filter_spec>/      ImageRenditionView
"""

from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet

from django.urls import re_path

from .api.views import (
    PageDetailView,
    PagePreviewView,
    AllPagesView,
    NavigationView,
    SettingsView,
    ThemeView,
    TowerDataView,
    InteractiveMapsView,
    GoogleMapsInstancesView,
    FormDetailView,
    FormSubmitView,
    InstagramFeedView,
    PromoBoxView,
    RebuildWebhookView,
    ImageRenditionView,
)

api_router = WagtailAPIRouter('wagtailapi')

api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)

headless_urls = [
    re_path(r'^api/v2/headless/pages/$', AllPagesView.as_view(), name='headless_all_pages'),
    re_path(r'^api/v2/headless/pages/(?P<page_id>\d+)/$', PageDetailView.as_view(), name='headless_page_detail'),
    re_path(r'^api/v2/headless/pages/by-slug/$', PageDetailView.as_view(), name='headless_page_by_slug'),
    re_path(r'^api/v2/headless/pages/preview/$', PagePreviewView.as_view(), name='headless_page_preview'),
    re_path(r'^api/v2/headless/navigation/$', NavigationView.as_view(), name='headless_navigation'),
    re_path(r'^api/v2/headless/settings/$', SettingsView.as_view(), name='headless_settings'),
    re_path(r'^api/v2/headless/themes/$', ThemeView.as_view(), name='headless_themes'),
    re_path(r'^api/v2/headless/towers/$', TowerDataView.as_view(), name='headless_towers'),
    re_path(r'^api/v2/headless/maps/$', InteractiveMapsView.as_view(), name='headless_maps'),
    re_path(r'^api/v2/headless/google-maps/$', GoogleMapsInstancesView.as_view(), name='headless_google_maps'),
    re_path(r'^api/v2/headless/forms/(?P<form_id>\d+)/$', FormDetailView.as_view(), name='headless_form_detail'),
    re_path(r'^api/v2/headless/forms/(?P<form_id>\d+)/submit/$', FormSubmitView.as_view(), name='headless_form_submit'),
    re_path(r'^api/v2/headless/instagram/$', InstagramFeedView.as_view(), name='headless_instagram'),
    re_path(r'^api/v2/headless/promobox/$', PromoBoxView.as_view(), name='headless_promobox'),
    re_path(r'^api/v2/headless/revalidate/$', RebuildWebhookView.as_view(), name='headless_revalidate'),
    re_path(r'^api/v2/headless/images/(?P<image_id>\d+)/(?P<filter_spec>.+)/$', ImageRenditionView.as_view(), name='headless_image_rendition'),
]

headless_urls_patterns = headless_urls
