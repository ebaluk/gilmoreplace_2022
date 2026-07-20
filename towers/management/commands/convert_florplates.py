import os
import json
from wagtail.models import Collection

from wagtail.images import get_image_model
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils import encoding
from django.utils.text import slugify
from unidecode import unidecode
from django.db import connection

from django.conf import settings
from towers.models import Tower
from willow.image import Image as Willow_Image
from PIL import Image as PIL_Image

IMAGES_FOLDER = 'original_images/keyplates'
Image = get_image_model()

class Command(BaseCommand):

    def handle(self, *args, **options):        

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, IMAGES_FOLDER)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, IMAGES_FOLDER))

        for tower in Tower.objects.all():

            for tower_plan in tower.plans.all():
                img = PIL_Image.open(tower_plan.floorplates_image.file)

                # tower_plan.floorplates_images = []
                stream_data = []

                print(tower.title, tower_plan.title)

                i = 0
                for row in range(0, 2):
                    for col in range(0, 4):
                        x = col * 159
                        y = row * 160 + 46
                        new_i = img.crop((x, y, x+159, y+160))

                        print((x, y, x+159, y+160))
                        print(new_i.size)
                        
                        if new_i.getbbox():
                            i += 1

                            title = "{}-{}-{}".format(tower.title, tower_plan.title, i)
                            print(title)
                            
                            fn = os.path.join(IMAGES_FOLDER, "{}.png".format(title))
                            new_i.save(os.path.join(settings.MEDIA_ROOT, fn))
                            image = None
                            try:
                                image = Image.objects.get(
                                    file = fn,
                                    title=title,
                                )
                            except Image.DoesNotExist:
                                image = Image(title=title)
                                image.file = fn
                                image.collection_id = 7
                                image.save()


                            

                            stream_data.append(
                                {
                                    'type': 'image', 
                                    'value': image.id                                
                                }
                            )

                tower_plan.floorplates_images = json.dumps(stream_data)
                tower_plan.save(force_update=True)


                        
