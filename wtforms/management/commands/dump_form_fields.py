import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Dump existing WtFormField (InlinePanel) data to JSON before migrating to StreamField."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help="Output file path (default: wtforms_fields_dump.json in project root).",
        )
        parser.add_argument(
            "--form-id",
            type=int,
            default=None,
            help="Dump only a specific form by ID.",
        )

    def handle(self, *args, **options):
        from wtforms.models import WtForm

        output_path = options["output"]
        if not output_path:
            output_path = os.path.join(settings.BASE_DIR, "wtforms_fields_dump.json")

        form_id = options["form_id"]

        qs = WtForm.objects.prefetch_related("form_fields").all()
        if form_id:
            qs = qs.filter(id=form_id)

        forms_data = []
        total_fields = 0

        for form in qs:
            fields = form.form_fields.order_by("sort_order")
            if not fields.exists():
                continue

            form_fields = []
            for f in fields:
                field_data = {
                    "sort_order": f.sort_order,
                    "field_type": f.field_type,
                    "label": f.label,
                    "show_label": f.show_label,
                    "required": f.required,
                    "default_value": f.default_value or "",
                    "help_text": f.help_text or "",
                    "add_css_class": f.add_css_class or "",
                    "placeholder": f.placeholder or "",
                    "related_input_class": f.related_input_class or "",
                    "lasso_field_name": f.lasso_field_name or "",
                    "choices": f.choices or "",
                    "lasso_question_list_id": f.lasso_question_list_id or None,
                }
                form_fields.append(field_data)
                total_fields += 1

            forms_data.append({
                "form_id": form.id,
                "form_name": form.name,
                "fields": form_fields,
            })

        dump = {
            "forms": forms_data,
            "exported_at": datetime.now().isoformat(),
            "total_forms": len(forms_data),
            "total_fields": total_fields,
        }

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=2, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Dumped {len(forms_data)} forms ({total_fields} fields) to {output_path}"
            )
        )
