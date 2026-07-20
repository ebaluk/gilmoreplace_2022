import json
import uuid
import os
import re
import unidecode
import urllib.request
from datetime import datetime
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from django.utils import encoding
from django.utils.text import slugify
from unidecode import unidecode
from django.db import migrations, models
from django.db import connection
import html
import requests
import lxml.html

from django.conf import settings

from interactivemaps.models import *


class Command(BaseCommand):

    # @transaction.atomic
    def handle(self, *args, **options):


        for cl in ['Tc', 'Sc']:
            for item in InteractiveMaps.objects.filter(title__contains='(En)'):
                title = item.title.replace('(En)', '({})'.format(cl))
                new_item = InteractiveMaps(
                    title = title,
                    layout_image = item.layout_image,
                )                
                for place in item.points.all():
                    new_item.points.create(
                        sort_order=place.sort_order,
                        title=place.title,
                        body=place.body,
                        left=place.left,
                        top=place.top,
                        visible=place.visible,
                    )                    
                    new_item.save()


                

        
        
        