from django.core.management.base import BaseCommand, CommandError
from wtinstagramtokens.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in WtInstagramToken.objects.all():
            item.fetch_in()
