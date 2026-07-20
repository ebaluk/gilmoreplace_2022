from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from towers.models import TowerPlanFloorPlateImageRendition





class Command(BaseCommand):

    def handle(self, *args, **options):        

        TowerPlanFloorPlateImageRendition.objects.all().delete()
