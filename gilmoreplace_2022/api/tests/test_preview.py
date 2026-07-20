from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from gilmoreplace_2022.api.page_urls import page_public_path
from wthomepage.models import LanguageRootPage
from wtpages.models import StandardPage


class PagePublicPathTests(TestCase):
    def test_language_root_path_is_relative_to_site_root(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        root = LanguageRootPage.objects.get(language_code="en-us")
        path = page_public_path(root)
        self.assertTrue(path.startswith("/"), path)
        self.assertTrue(path.endswith("/"), path)
        self.assertIn(root.slug, path)

    def test_wagtail_serve_reverse_still_registered(self):
        self.assertEqual(reverse("wagtail_serve", args=("en/",)), "/en/")


@override_settings(PREVIEW_SECRET="test-preview-secret")
class PagePreviewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_preview_requires_secret(self):
        response = self.client.get(
            "/api/v2/headless/pages/preview/",
            {"content_type": "wtpages.standardpage", "token": "x"},
        )
        self.assertEqual(response.status_code, 404)

    def test_preview_rejects_bad_secret(self):
        response = self.client.get(
            "/api/v2/headless/pages/preview/",
            {"content_type": "wtpages.standardpage", "token": "x"},
            HTTP_X_PREVIEW_SECRET="wrong",
        )
        self.assertEqual(response.status_code, 404)

    def test_preview_with_valid_token_returns_draft_payload(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        page = (
            StandardPage.objects.live()
            .descendant_of(LanguageRootPage.objects.get(language_code="en-us"))
            .first()
        )
        if page is None:
            self.skipTest("No StandardPage available for preview test")

        specific = page.specific
        preview = specific.create_page_preview()

        response = self.client.get(
            "/api/v2/headless/pages/preview/",
            {
                "content_type": specific.get_content_type_str(),
                "token": preview.token,
            },
            HTTP_X_PREVIEW_SECRET="test-preview-secret",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], page.id)
        self.assertTrue(data["url"].startswith("/"))
        # Preview must not silently follow redirect_to_first_child.
        if getattr(specific, "redirect_to_first_child", False):
            self.assertEqual(data["content_page_id"], page.id)
            self.assertFalse(data["redirect_to_first_child"])


class SettingsUrlsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_language_roots_have_string_urls(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        # Even without relying on Page.get_url(), settings must validate.
        response = self.client.get(
            "/api/v2/headless/settings/",
            {"locale": "en-us"},
        )
        self.assertEqual(response.status_code, 200)
        for root in response.json().get("language_roots", []):
            self.assertIsInstance(root.get("url"), str)
            self.assertTrue(root["url"].startswith("/"))
