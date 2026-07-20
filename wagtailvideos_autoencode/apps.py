from django.apps import AppConfig


class WagtailvideosAutoencodeConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "wagtailvideos_autoencode"
    verbose_name = "Wagtail Videos Auto-encode"

    def ready(self):
        from . import signals  # noqa: F401
