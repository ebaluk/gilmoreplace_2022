import hashlib
from unidecode import unidecode
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock


def make_clean_name(label, index):
    """Generate a unique clean_name for a form field block."""
    slug = slugify(str(unidecode(label or "field")))
    short_hash = hashlib.md5(f"{label}{index}".encode()).hexdigest()[:8]
    return f"{slug}-{short_hash}"


def make_clean_name_2(label):
    """Generate clean_name_2 (without unique suffix) for Lasso field mapping."""
    return str(slugify(str(unidecode(label))))


class FormFieldBaseBlock(blocks.StructBlock):
    """Base block with fields shared by all form field types."""

    label = blocks.TextBlock(label=_("Label"))
    show_label = blocks.BooleanBlock(default=True, required=False, label=_("Show label"))
    required = blocks.BooleanBlock(default=True, required=False, label=_("Required"))
    default_value = blocks.CharBlock(required=False, label=_("Default value"))
    help_text = blocks.TextBlock(required=False, label=_("Help text"))
    add_css_class = blocks.CharBlock(required=False, label=_("Add CSS class"))
    placeholder = blocks.CharBlock(required=False, label=_("Placeholder"))
    related_input_class = blocks.CharBlock(required=False, label=_("Related Input Name"))

    # Lasso CRM
    lasso_field_name = blocks.CharBlock(required=False, label=_("Lasso Field Name"))

    class Meta:
        label = None
        template = "wtforms/blocks/form_field_block.html"


class FormFieldWithChoicesBlock(FormFieldBaseBlock):
    """Base block for field types that have choices (dropdown, radio, checkboxes)."""

    choices = blocks.TextBlock(
        required=False,
        label=_("Choices"),
        help_text=_("New line separated list of choices."),
    )
    lasso_question_list = SnippetChooserBlock(
        "wtforms.WtFormLassoList",
        required=False,
        label=_("Lasso Question List"),
    )

    class Meta:
        label = None


# --- Concrete field blocks ---

class SingleLineFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Single line text")


class MultiLineFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Multi-line text")


class EmailFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Email")


class NumberFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Number")


class URLFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("URL")


class DateFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Date")


class TimeFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Time")


class DateTimeFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Date/time")


class CheckboxFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Checkbox")


class DropdownFieldBlock(FormFieldWithChoicesBlock):
    class Meta:
        label = _("Drop down")


class RadioFieldBlock(FormFieldWithChoicesBlock):
    class Meta:
        label = _("Radio buttons")


class CheckboxesFieldBlock(FormFieldWithChoicesBlock):
    class Meta:
        label = _("Checkboxes")


class FileFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("File upload")


class CaptchaFieldBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Captcha")


class FieldsGroupBlock(FormFieldBaseBlock):
    class Meta:
        label = _("Fields Group")


class SectionTitleH2Block(FormFieldBaseBlock):
    class Meta:
        label = _("Section Title H2")


class SectionTitleH3Block(FormFieldBaseBlock):
    class Meta:
        label = _("Section Title H3")


# --- StreamField block list for WtForm.form_body ---

WTFORMS_BLOCKS = [
    ("singleline", SingleLineFieldBlock()),
    ("multiline", MultiLineFieldBlock()),
    ("email", EmailFieldBlock()),
    ("number", NumberFieldBlock()),
    ("url", URLFieldBlock()),
    ("date", DateFieldBlock()),
    ("time", TimeFieldBlock()),
    ("datetime", DateTimeFieldBlock()),
    ("checkbox", CheckboxFieldBlock()),
    ("dropdown", DropdownFieldBlock()),
    ("radio", RadioFieldBlock()),
    ("checkboxes", CheckboxesFieldBlock()),
    ("file", FileFieldBlock()),
    ("captcha", CaptchaFieldBlock()),
    ("fieldsgroup", FieldsGroupBlock()),
    ("sectiontitleh2", SectionTitleH2Block()),
    ("sectiontitleh3", SectionTitleH3Block()),
]


# --- Block type to field_type mapping ---

BLOCK_TYPE_TO_FIELD_TYPE = {
    "singleline": "singleline",
    "multiline": "multiline",
    "email": "email",
    "number": "number",
    "url": "url",
    "date": "date",
    "time": "time",
    "datetime": "datetime",
    "checkbox": "checkbox",
    "dropdown": "dropdown",
    "radio": "radio",
    "checkboxes": "checkboxes",
    "file": "file",
    "captcha": "captcha",
    "fieldsgroup": "fieldsgroup",
    "sectiontitleh2": "sectiontitleh2",
    "sectiontitleh3": "sectiontitleh3",
}


class FormFieldBlockAdapter:
    """
    Adapts a StreamField block + index to quack like a WtAbstractFormField ORM object.

    Used by WtFormBuilder, serialize_form_field, resolve_form_field_choices,
    and process_form_submission — all of which access field attributes via dot notation.
    """

    def __init__(self, block_type, value, index):
        self.block_type = block_type
        self.field_type = BLOCK_TYPE_TO_FIELD_TYPE.get(block_type, block_type)
        self._value = value
        self._index = index
        self.id = index
        self.pk = index

    @property
    def label(self):
        return self._value.get("label", "")

    @property
    def show_label(self):
        return self._value.get("show_label", True)

    @property
    def required(self):
        return self._value.get("required", True)

    @property
    def default_value(self):
        return self._value.get("default_value", "")

    @property
    def help_text(self):
        return self._value.get("help_text", "")

    @property
    def add_css_class(self):
        return self._value.get("add_css_class", "")

    @property
    def placeholder(self):
        return self._value.get("placeholder", "")

    @property
    def related_input_class(self):
        return self._value.get("related_input_class", "")

    @property
    def lasso_field_name(self):
        return self._value.get("lasso_field_name", "")

    @property
    def lasso_question_list_id(self):
        return self._value.get("lasso_question_list")

    @property
    def lasso_question_list(self):
        lid = self.lasso_question_list_id
        if not lid:
            return None
        return _lazy_lasso_list_loader(lid)

    @property
    def choices(self):
        return self._value.get("choices", "")

    @property
    def clean_name(self):
        legacy = self._value.get("_legacy_clean_name")
        if legacy:
            return legacy
        return make_clean_name(self.label, self._index)

    @property
    def clean_name_2(self):
        return make_clean_name_2(self.label)

    @property
    def clean_related_input_name(self):
        rc = self.related_input_class
        return str(slugify(str(unidecode(rc)))) if rc else None

    def __str__(self):
        return self.label


# Cache for lazy lasso list loading to avoid N+1 queries
_lasso_list_cache: dict = {}


def _lazy_lasso_list_loader(lasso_list_id):
    if lasso_list_id not in _lasso_list_cache:
        from wtforms.models import WtFormLassoList
        try:
            obj = WtFormLassoList.objects.prefetch_related("list_items").get(id=lasso_list_id)
            _lasso_list_cache[lasso_list_id] = obj
        except WtFormLassoList.DoesNotExist:
            return None
    return _lasso_list_cache[lasso_list_id]


def iter_form_field_blocks(stream_value, include_meta=True):
    """
    Yield (block_type, block_value, index) tuples from a StreamField's raw_data.

    If stream_value is a StreamValue (has raw_data), use raw_data for efficiency.
    Otherwise iterate the StreamField directly.
    """
    try:
        raw = stream_value.raw_data
    except AttributeError:
        for idx, block in enumerate(stream_value, start=1):
            yield FormFieldBlockAdapter(block.block_type, block.value, idx)
        return

    if not raw:
        return

    for idx, item in enumerate(raw, start=1):
        block_type = item.get("type", "")
        value = item.get("value", {})
        if isinstance(value, str):
            value = {}
        yield FormFieldBlockAdapter(block_type, value, idx)
