import json
import uuid
#from django.db import transaction
from django.core.management.base import BaseCommand

from wagtail.images import get_image_model


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        Image = get_image_model()        
        images = Image.objects.all()
        for image in images:
            image.tags.add(image.collection.name)
            image.save()

            