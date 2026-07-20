from django.test import TestCase
from rest_framework.test import APIClient

from wtforms.models import WtForm


class FormDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.form = WtForm.objects.create(
            name="Test Form",
            title="Contact",
            enable_recaptcha=False,
        )
        cls.form.form_body = [
            {
                "type": "singleline",
                "value": {
                    "_legacy_clean_name": "first-name-1",
                    "label": "First Name",
                    "show_label": True,
                    "required": True,
                    "default_value": "",
                    "help_text": "",
                    "add_css_class": "col-sm-6",
                    "placeholder": "",
                    "related_input_class": "",
                    "lasso_field_name": "",
                },
                "id": "aaaaaaa1",
            },
            {
                "type": "email",
                "value": {
                    "_legacy_clean_name": "email-2",
                    "label": "Email",
                    "show_label": True,
                    "required": True,
                    "default_value": "",
                    "help_text": "",
                    "add_css_class": "col-sm-6",
                    "placeholder": "",
                    "related_input_class": "",
                    "lasso_field_name": "",
                },
                "id": "aaaaaaa2",
            },
        ]
        cls.form.use_streamfield = True
        cls.form.save()

    def test_returns_200_for_valid_form(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        self.assertEqual(response.status_code, 200)

    def test_returns_form_structure(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        data = response.json()

        self.assertEqual(data["id"], self.form.id)
        self.assertEqual(data["title"], "Contact")
        self.assertIn("submit_url", data)

    def test_returns_fields_array(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        data = response.json()

        self.assertIn("fields", data)
        self.assertEqual(len(data["fields"]), 2)

    def test_field_has_required_props(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        fields = response.json()["fields"]

        first = fields[0]
        self.assertIn("id", first)
        self.assertIn("label", first)
        self.assertIn("field_type", first)
        self.assertIn("required", first)
        self.assertIn("clean_name", first)
        self.assertIn("choices", first)
        self.assertIn("choices_list", first)
        self.assertIn("default_value", first)
        self.assertIn("help_text", first)
        self.assertIn("add_css_class", first)
        self.assertIn("num", first)

    def test_field_clean_name_preserved(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        fields = response.json()["fields"]

        self.assertEqual(fields[0]["clean_name"], "first-name-1")
        self.assertEqual(fields[0]["field_type"], "singleline")
        self.assertEqual(fields[1]["clean_name"], "email-2")
        self.assertEqual(fields[1]["field_type"], "email")

    def test_404_for_nonexistent_form(self):
        response = self.client.get("/api/v2/headless/forms/99999/")
        self.assertEqual(response.status_code, 404)

    def test_includes_enable_recaptcha(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        data = response.json()
        self.assertIn("enable_recaptcha", data)
        self.assertFalse(data["enable_recaptcha"])

    def test_includes_recaptcha_site_key(self):
        response = self.client.get(f"/api/v2/headless/forms/{self.form.id}/")
        data = response.json()
        self.assertIn("recaptcha_site_key", data)


class FormSubmitViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.form = WtForm.objects.create(
            name="Submit Test Form",
            title="Registration",
            enable_recaptcha=False,
            thank_you_text="<p>Thanks!</p>",
        )
        cls.form.form_body = [
            {
                "type": "singleline",
                "value": {
                    "_legacy_clean_name": "name-1",
                    "label": "Name",
                    "show_label": True,
                    "required": True,
                    "default_value": "",
                    "help_text": "",
                    "add_css_class": "",
                    "placeholder": "",
                    "related_input_class": "",
                    "lasso_field_name": "",
                },
                "id": "bbbbbbb1",
            },
            {
                "type": "email",
                "value": {
                    "_legacy_clean_name": "email-2",
                    "label": "Email",
                    "show_label": True,
                    "required": True,
                    "default_value": "",
                    "help_text": "",
                    "add_css_class": "",
                    "placeholder": "",
                    "related_input_class": "",
                    "lasso_field_name": "",
                },
                "id": "bbbbbbb2",
            },
        ]
        cls.form.use_streamfield = True
        cls.form.save()

    def test_submit_url_returns_200(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"name-1": "John", "email-2": "john@example.com"},
        )
        self.assertEqual(response.status_code, 200)

    def test_successful_submit_returns_status_success(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"name-1": "John", "email-2": "john@example.com"},
        )
        self.assertEqual(response.json()["status"], "success")

    def test_successful_submit_returns_thank_you_text(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"name-1": "John", "email-2": "john@example.com"},
        )
        self.assertIn("message_text", response.json())

    def test_successful_submit_returns_message_title(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"name-1": "John", "email-2": "john@example.com"},
        )
        self.assertIn("message_title", response.json())

    def test_missing_required_field_returns_error(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"email-2": "john@example.com"},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("errors", data)

    def test_missing_all_fields_returns_errors(self):
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("name-1", data.get("errors", {}))
        self.assertIn("email-2", data.get("errors", {}))

    def test_404_for_nonexistent_form(self):
        response = self.client.post(
            "/api/v2/headless/forms/99999/submit/",
            {"name": "John"},
        )
        self.assertEqual(response.status_code, 404)

    def test_successful_submit_creates_submission(self):
        from wtforms.models import WtFormSubmission
        response = self.client.post(
            f"/api/v2/headless/forms/{self.form.id}/submit/",
            {"name-1": "John Doe", "email-2": "john@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            WtFormSubmission.objects.filter(page=self.form).exists()
        )

    def test_form_with_recaptcha_returns_200_on_submit(self):
        form = WtForm.objects.create(
            name="Captcha Form",
            enable_recaptcha=True,
        )
        form.form_body = [
            {
                "type": "singleline",
                "value": {
                    "_legacy_clean_name": "test-1",
                    "label": "Test",
                    "show_label": True,
                    "required": False,
                    "default_value": "",
                    "help_text": "",
                    "add_css_class": "",
                    "placeholder": "",
                    "related_input_class": "",
                    "lasso_field_name": "",
                },
                "id": "ccccccc1",
            },
        ]
        form.use_streamfield = True
        form.save()

        response = self.client.post(
            f"/api/v2/headless/forms/{form.id}/submit/",
            {"test-1": "Hello"},
        )
        self.assertEqual(response.status_code, 400)
