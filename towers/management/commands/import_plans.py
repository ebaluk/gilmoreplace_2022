from wagtail.documents.models import Document
from wagtail.images.models import Image
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

from towers.models import *


data = [
    {'title': '1', 'view_collection_id': 9, 'url': "https://sheets.googleapis.com/v4/spreadsheets/12C_7zZfZ5JJHaLBbK8L_No3WZd38yEPIDzjg774u1zs/values/Tower%201?alt=json&key=AIzaSyAqR2sctE-7nC8BNPeDMz7LkLC5LOFchGA"},
    {'title': '2', 'view_collection_id': 10, 'url': "https://sheets.googleapis.com/v4/spreadsheets/12C_7zZfZ5JJHaLBbK8L_No3WZd38yEPIDzjg774u1zs/values/Tower%202?alt=json&key=AIzaSyAqR2sctE-7nC8BNPeDMz7LkLC5LOFchGA"},
    {'title': '3', 'view_collection_id': 11, 'url': "https://sheets.googleapis.com/v4/spreadsheets/12C_7zZfZ5JJHaLBbK8L_No3WZd38yEPIDzjg774u1zs/values/Tower%203?alt=json&key=AIzaSyAqR2sctE-7nC8BNPeDMz7LkLC5LOFchGA"},
]


class Command(BaseCommand):


    def handle(self, *args, **options):        

        return
        
        Tower.objects.all().delete()
        
        for tower in data:            
            r = requests.get(tower['url'])
            print(tower['title'])
            tower_instance = Tower(
                title = tower['title'],
            )
            sort_order = 0
            
            plans = r.json()
            for item in plans['values'][1:]:
                if item[4] != "Available":
                    continue

                try:                        
                    bt = TowerBedroomTypes.objects.get(title=item[3])
                except TowerBedroomTypes.DoesNotExist:
                    bt = TowerBedroomTypes(title=item[3])
                    bt.save()

                image_name = "{}-{}".format(tower['title'], item[2])     
                print(item[2], image_name)

                floorplates_image = Image.objects.get(title__iexact=image_name, collection__id=7)                
                floorplan_image = Image.objects.get(title__iexact=image_name, collection__id=5)                
                pdf = Document.objects.get(title__iexact=image_name, collection__id=5)

                try:
                    tower_instance.plans.get(title = item[2])
                except TowerPlan.DoesNotExist:    
                    tower_instance.plans.create(
                        sort_order = sort_order,
                        title = item[2],                    
                        pdf = pdf,                    
                        floorplates_image = floorplates_image,
                        floorplan_image = floorplan_image,
                        bedrooms = bt,                    
                        interiors = item[5].replace(" ", "").replace(",", ""),
                        exteriors = item[6].replace(" ", "").replace(",", ""),
                    )
                    sort_order += 1


            sort_order = 0
            for image in Image.objects.filter(collection__id=tower['view_collection_id']).extra(
                    select={'int_title': 'CAST(title AS INTEGER)'}
                ).order_by('int_title'):
                tower_instance.views.create(
                    sort_order = sort_order,
                    title = image.title,
                    image = image,                                        
                )
                sort_order += 1

            tower_instance.save()    
                

                