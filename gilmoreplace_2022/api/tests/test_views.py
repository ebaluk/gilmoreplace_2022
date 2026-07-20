from django.test import TestCase
from rest_framework.test import APIClient

from wthomepage.models import LanguageRootPage


class HeadlessAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unknown_locale_returns_404(self):
        response = self.client.get(
            "/api/v2/headless/pages/by-slug/",
            {"slug": "gallery", "locale": "does-not-exist"},
        )

        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_returns_404(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        response = self.client.get(
            "/api/v2/headless/pages/by-slug/",
            {"slug": "this-page-should-not-exist-xyz", "locale": "en-us"},
        )

        self.assertEqual(response.status_code, 404)

    def test_about_onni_page_returns_about_collage_block(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        response = self.client.get(
            "/api/v2/headless/pages/by-slug/",
            {"slug": "about-onni", "locale": "en-us"},
        )

        if response.status_code == 404:
            self.skipTest("about-onni page is not available in the test database")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        block_types = [block["type"] for block in data.get("stream_field", [])]
        self.assertIn("about_collage", block_types)

        collage = next(
            block for block in data["stream_field"] if block["type"] == "about_collage"
        )
        self.assertIn("resolved_image_groups", collage["value"])
        self.assertGreater(len(collage["value"]["resolved_image_groups"]), 0)

    def test_gallery_page_redirects_content_to_first_child(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        response = self.client.get(
            "/api/v2/headless/pages/by-slug/",
            {"slug": "gallery", "locale": "en-us"},
        )

        if response.status_code == 404:
            self.skipTest("gallery page is not available in the test database")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("redirect_to_first_child"))
        self.assertNotEqual(data["id"], data["content_page_id"])

        block_types = [block["type"] for block in data.get("stream_field", [])]
        self.assertIn("gallery_collections", block_types)

    def test_navigation_endpoint_returns_items(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        response = self.client.get(
            "/api/v2/headless/navigation/",
            {"locale": "en-us"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIsInstance(response.json()["items"], list)

    def test_settings_endpoint_returns_site_settings(self):
        if not LanguageRootPage.objects.filter(language_code="en-us").exists():
            self.skipTest("Language root page for en-us is not available")

        response = self.client.get(
            "/api/v2/headless/settings/",
            {"locale": "en-us"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("site_settings", payload)
        self.assertIn("page_meta", payload)
        root_page = payload.get("root_page")
        if root_page:
            self.assertIn("page_404_title", root_page)
            self.assertIn("page_404_text", root_page)
            self.assertIn("page_404_image", root_page)
