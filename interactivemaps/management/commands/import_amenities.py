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


data = {
    2: {
        
            "list": [
            "Party Room",
            "Study Room",
            "Games Room",
            "Main Gym",
            "Golf Simulator",
            "Cardio Gym",
            "Change Rooms",
            "Main Lounge",
            "Bowling Lanes",
            "Outdoor Terrace",
            "Movie Theatre",
            "Steam Room + Sauna",
            "Indoor Pool + Hydrotherapy Pools",
            "Hot Tub",
            "Sports Court",
            "Workshop",
            "Guest Suites",
            "Party Room",
            "Children's Indoor Play Area",
            "Dog Park"
        ],

        'hotspots': [

            {              
              'loc': ["28.58", "13.23"]
            },
            {
             
              'loc': ["18.01", "13.77"]
            },
            {
             
              'loc': ["7.33", "20.23"]
            },
            {
             
              'loc': ["32.94", "31.46"]
            },
            {
             
              'loc': ["7.33", "36.38"]
            },
            {
             
              'loc': ["48.55", "33.23"]
            },
            {
             
              'loc': ["23.88", "46.31"]
            },
            {
             
              'loc': ["9.84", "48.62"]
            },
            {
             
              'loc': ["18.46", "59.23"]
            },
            {
             
              'loc': ["2.13", "56.23"]
            },
            {
             
              'loc': ["12.36", "67.15"]
            },
            {
             
              'loc': ["23.88", "65.23"]
            },
            {
             
              'loc': ["31.49", "64.38"]
            },
            {
             
              'loc': ["33.17", "75"]
            },
            {
             
              'loc': ["49.72", "55.08"]
            },
            {
             
              'loc': ["55.59", "42.54"]
            },
            {
             
              'loc': ["28.08", "83.69"]
            },
            {
             
              'loc': ["14.26", "89.38"]
            },
            {
             
              'loc': ["4.75", "79.92"]
            },
            {
             
              'loc': ["82.77", "13.69"]
            }
          ]
        
    },

    3: {
        "list": [
          "Hot Tub",
          "Outdoor Pool",
          "Outdoor Fireplace + Lounge",
          "Children's Play Area",
          "Urban Garden Plots",
          "Bocce Lawn",
          "Fire Pit",
          "BBQ Area",
          "BBQ Area",
          "BBQ Area",
          "BBQ Area"
        ],
        'hotspots': [
            {
              
              'loc': ["5.41", "50"]
            },
            {
              
              'loc': ["14.33", "61.58"]
            },
            {
              
              'loc': ["40.5", "33.59"]
            },
            {
              
              'loc': ["70.91", "41.51"]
            },
            {
              
              'loc': ["76.61", "55.21"]
            },
            {
              
              'loc': ["44.01", "59.46"]
            },
            {
              
              'loc': ["38.89", "90.54"]
            },
            {
              
              'loc': ["45.91", "11.2"]
            },
            {
              
              'loc': ["44.01", "43.63"]
            },
            {
              
              'loc': ["61.70", "61.97"]
            },
            {
              
              'loc': ["45.91", "75.68"]
            }
          ]
    }
    
    
}


class Command(BaseCommand):

    # @transaction.atomic
    def handle(self, *args, **options):
        
        sort_order = 0
        for id, map in data.items():            
            instance = InteractiveMaps.objects.get(id=id)
            instance.points.all().delete()
            sort_order = 0
            for item in map['hotspots']:
                instance.points.create(
                    sort_order = sort_order,                    
                    left = float(item['loc'][0]),
                    top = float(item['loc'][1]),
                    title = map['list'][sort_order],
                )
                sort_order += 1
            instance.save()    
