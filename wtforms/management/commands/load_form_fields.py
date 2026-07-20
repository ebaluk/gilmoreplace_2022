import json
import uuid
from unidecode import unidecode
from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Load form fields from a JSON dump into WtForm.form_body StreamField."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            default=None,
            help="Input JSON file path (default: wtforms_fields_dump.json in project root).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Show what would be done without saving.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Overwrite existing form_body data if already set.",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        input_path = options["input"]
        if not input_path:
            input_path = settings.BASE_DIR + "/wtforms_fields_dump.json"

        dry_run = options["dry_run"]
        force = options["force"]

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                dump = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {input_path}"))
            return
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"Invalid JSON: {e}"))
            return

        forms_data = dump.get("forms", [])
        if not forms_data:
            self.stderr.write(self.style.WARNING("No forms found in dump file."))
            return

        from wtforms.models import WtForm

        updated = 0
        skipped = 0
        total_fields = 0

        for form_entry in forms_data:
            form_id = form_entry["form_id"]
            form_name = form_entry.get("form_name", "Unknown")

            try:
                form = WtForm.objects.get(id=form_id)
            except WtForm.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(f"Form #{form_id} ({form_name}) not found — skipping.")
                )
                skipped += 1
                continue

            if form.use_streamfield and form.form_body and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"Form #{form_id} ({form_name}) already has StreamField data — skipping (use --force to overwrite)."
                    )
                )
                skipped += 1
                continue

            raw_fields = form_entry.get("fields", [])
            if not raw_fields:
                self.stdout.write(
                    self.style.WARNING(f"Form #{form_id} ({form_name}) has no fields — skipping.")
                )
                skipped += 1
                continue

            stream_data = []
            for f in sorted(raw_fields, key=lambda x: x.get("sort_order", 0)):
                label = f.get("label") or "field"
                index = f.get("sort_order", 0) + 1

                clean_name = "%s-%s" % (slugify(str(unidecode(label))), index)

                value = {
                    "_legacy_clean_name": clean_name,
                    "label": label,
                    "show_label": f.get("show_label", True),
                    "required": f.get("required", True),
                    "default_value": f.get("default_value") or "",
                    "help_text": f.get("help_text") or "",
                    "add_css_class": f.get("add_css_class") or "",
                    "placeholder": f.get("placeholder") or "",
                    "related_input_class": f.get("related_input_class") or "",
                    "lasso_field_name": f.get("lasso_field_name") or "",
                }

                field_type = f.get("field_type", "singleline")
                if field_type in ("dropdown", "radio", "checkboxes"):
                    value["choices"] = f.get("choices") or ""
                    lasso_id = f.get("lasso_question_list_id")
                    if lasso_id:
                        value["lasso_question_list"] = lasso_id

                stream_data.append({
                    "type": field_type,
                    "value": value,
                    "id": uuid.uuid4().hex,
                })
                total_fields += 1

            if dry_run:
                self.stdout.write(
                    f"[DRY-RUN] Form #{form_id} ({form_name}): "
                    f"would write {len(stream_data)} fields to form_body, set use_streamfield=True"
                )
            else:
                form.form_body = stream_data
                form.use_streamfield = True
                form.save(update_fields=["form_body", "use_streamfield"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Form #{form_id} ({form_name}): {len(stream_data)} fields loaded."
                    )
                )

            updated += 1

        verb = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{verb} {updated} forms ({total_fields} fields), skipped {skipped}."
            )
        )
