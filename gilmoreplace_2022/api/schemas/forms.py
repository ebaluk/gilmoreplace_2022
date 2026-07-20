"""Form detail and submit response schemas."""

from __future__ import annotations

from typing import Any

from .common import ApiModel


class FormFieldChoice(ApiModel):
    value: str
    label: str


class FormFieldSchema(ApiModel):
    id: int | None = None
    label: str = ""
    field_type: str = ""
    required: bool = False
    choices: str | None = None
    choices_list: list[FormFieldChoice] | None = None
    default_value: str | None = None
    help_text: str | None = None
    clean_name: str = ""
    add_css_class: str | None = None
    num: int | None = None


class FormDetailResponse(ApiModel):
    """GET /api/v2/headless/forms/<id>/"""

    id: int
    title: str = ""
    submit_url: str = ""
    fields: list[FormFieldSchema] = []
    recaptcha_site_key: str = ""
    enable_recaptcha: bool = False


class FormSubmitResult(ApiModel):
    """POST /api/v2/headless/forms/<id>/submit/ response body."""

    status: str
    message_text: str | None = None
    message_title: str | None = None
    call_js_on_success: Any = None
    thank_you_url: str | None = None
    error: str | None = None
    errors: dict[str, list[str]] | None = None
