"""Unit tests for Pydantic headless API schemas."""

from django.test import SimpleTestCase

from gilmoreplace_2022.api.schemas import (
    FormSubmitResult,
    PageResponse,
    SettingsResponse,
    dump_model,
)


class SettingsSchemaTests(SimpleTestCase):
    def test_settings_payload_validates(self):
        payload = {
            "site_settings": {"caption": "x", "logo": None, "ga_view_id": 1},
            "page_meta": {"site_name": "Gilmore Place"},
            "root_page": None,
            "language_roots": [
                {"language_code": "en-us", "url": "/en/", "label": "EN"},
            ],
        }
        data = dump_model(SettingsResponse, payload)
        self.assertEqual(data["language_roots"][0]["language_code"], "en-us")


class FormSubmitSchemaTests(SimpleTestCase):
    def test_success_and_error_payloads(self):
        ok = dump_model(
            FormSubmitResult,
            {"status": "success", "message_title": "Thanks", "thank_you_url": None},
        )
        self.assertEqual(ok["status"], "success")
        err = dump_model(
            FormSubmitResult,
            {"status": "error", "errors": {"email": ["Required"]}},
        )
        self.assertEqual(err["errors"]["email"], ["Required"])


class PageSchemaTests(SimpleTestCase):
    def test_page_allows_extra_stream(self):
        payload = {
            "id": 1,
            "title": "Home",
            "slug": "home",
            "stream_field": [{"type": "paragraph", "value": {"text": "hi"}}],
            "hero": {"title": "Home"},
            "unknown_future_field": 123,
        }
        data = dump_model(PageResponse, payload)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["stream_field"][0]["type"], "paragraph")
