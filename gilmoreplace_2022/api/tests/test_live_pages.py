from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from wthomepage.models import LanguageRootPage
from wtpages.models import StandardPage


class PageDetailLiveOnlyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unpublished_page_by_id_returns_404(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        page = (
            StandardPage.objects.live()
            .descendant_of(LanguageRootPage.objects.get(language_code="en-us"))
            .first()
        )
        if page is None:
            self.skipTest("No live StandardPage available")

        page.unpublish()

        response = self.client.get(f"/api/v2/headless/pages/{page.id}/")
        self.assertEqual(response.status_code, 404)

    def test_unpublished_page_by_slug_returns_404(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        page = (
            StandardPage.objects.live()
            .descendant_of(LanguageRootPage.objects.get(language_code="en-us"))
            .first()
        )
        if page is None:
            self.skipTest("No live StandardPage available")

        slug = page.slug
        page.unpublish()

        response = self.client.get(
            "/api/v2/headless/pages/by-slug/",
            {"slug": slug, "locale": "en-us"},
        )
        self.assertEqual(response.status_code, 404)


@override_settings(PREVIEW_SECRET="test-preview-secret")
class PreviewSecretTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_preview_query_secret_is_ignored(self):
        response = self.client.get(
            "/api/v2/headless/pages/preview/",
            {
                "content_type": "wtpages.standardpage",
                "token": "x",
                "secret": "test-preview-secret",
            },
        )
        self.assertEqual(response.status_code, 404)
