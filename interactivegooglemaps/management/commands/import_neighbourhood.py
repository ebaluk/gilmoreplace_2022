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

from interactivegooglemaps.models import *


data = [
    {
        'title': 'Food',
        'color': "#6660AA",
        'places': [
            {'name': "JOEY Burnaby", 'lat': 49.2669341, 'lng': -123.0066938},
            {'name': "Cactus Club Cafe", 'lat': 49.266695,
                'lng': -123.01086299999997},
            {'name': "Sushi Garden Lougheed",
                'lat': 49.26689, 'lng': -123.00902300000001},
            {'name': "Boston Pizza", 'lat': 49.25846250000001, 'lng': -123.030667},
            {
                'name': "Browns Socialhouse Brentwood",
                'lat': 49.2668955,
                'lng': -123.0056596
            },
            {
                'name': "Earls Kitchen + Bar",
                'lat': 49.26537099999999,
                'lng': -123.01964199999998
            },
            {'name': "White Spot", 'lat': 49.2663969, 'lng': -123.01393680000001},
            {'name': "Tim Hortons", 'lat': 49.2665391, 'lng': -123.01228789999999},
            {'name': "Kita Sushi", 'lat': 49.26429, 'lng': -123.01284900000002},
            {
                'name': "The Keg Steakhouse + Bar",
                'lat': 49.259669,
                'lng': -123.00189699999999
            },
            {'name': "Starbucks", 'lat': 49.2642731, 'lng': -123.0137929}
        ]
    },

    {
        'title': 'Grocery',
        'color': "#2150A3",
        'places': [
            {'name': "Costco Wholesale", 'lat': 49.2602546,
                'lng': -122.99917579999999},
            {'name': "Save-On-Foods", 'lat': 49.2668858, 'lng': -123.00799770000003},
            {'name': "Whole Foods Market", 'lat': 49.2662121,
                'lng': -123.00481990000003},
            {'name': "Pro Organics", 'lat': 49.2604744, 'lng': -123.00203069999998},
            {
                'name': "Real Canadian Superstore",
                'lat': 49.25908889999999,
                'lng': -123.03602130000002
            },
            {
                'name': "BC Liquor Stores",
                'lat': 49.26602080000001,
                'lng': -123.00518369999998
            },
            {'name': "Koby's Produce Town", 'lat': 49.2672359, 'lng': -123.0057933}
        ]
    },

    {
        'title': 'Shop',
        'color': "#7DA3D6",
        'places': [
            {
                'name': "Brentwood Town Centre",
                'lat': 49.2684831,
                'lng': -123.00079440000002
            },
            {'name': "The Home Depot", 'lat': 49.2631094, 'lng': -123.01693319999998},
            {'name': "Staples Lougheed", 'lat': 49.267066,
                'lng': -123.00940989999998},
            {
                'name': "Walmart Grandview Supercentre",
                'lat': 49.2591695,
                'lng': -123.02695640000002
            },
            {'name': "Winners", 'lat': 49.2668594, 'lng': -123.00663109999999},
            {'name': "Shoppers Drug Mart", 'lat': 49.2661883, 'lng': -123.0043139},
            {
                'name': "The Woof Burnaby",
                'lat': 49.26880569999999,
                'lng': -123.01660900000002
            }
        ]
    },

    {
        'title': 'Recreation',
        'color': "#3b9c52",
        'places': [
            {
                'name': "Burnaby Lake Sports Complex West",
                'lat': 49.253013,
                'lng': -122.96958010000003
            },
            {'name': "Brentwood Park", 'lat': 49.271402, 'lng': -122.995842},
            {'name': "Jim Lorimer Park", 'lat': 49.2628411,
                'lng': -123.01364309999997},
            {'name': "Beecher Park", 'lat': 49.273666, 'lng': -122.98906199999999},
            {
                'name': "Willingdon Heights Park",
                'lat': 49.2717389,
                'lng': -123.01313809999999
            },
            {'name': "Charles Park", 'lat': 49.2734348, 'lng': -123.02819399999998},
            {'name': "Rupert Park Pitch & Putt",
             'lat': 49.2730065, 'lng': -123.0308263},
            {
                'name': "Steve Nash Fitness World & Sports Club",
                'lat': 49.267195,
                'lng': -123.01193920000003
            }
        ]
    },

    {
        'title': 'Financials',
        'color': "#F15B29",
        'places': [
            {
                'name': "BMO Bank of Montreal",
                'lat': 49.26840480000001,
                'lng': -123.00042810000002
            },
            {'name': "CIBC ATM", 'lat': 49.26681319999999,
                'lng': -123.00369180000001},
            {'name': "CIBC Branch with ATM", 'lat': 49.268404, 'lng': -123.0012969},
            {'name': "TD Canada Trust", 'lat': 49.2671202,
                'lng': -123.00347679999999},
            {'name': "Scotiabank", 'lat': 49.2682885, 'lng': -123.00102859999998},
            {'name': "HSBC Bank", 'lat': 49.2667539, 'lng': -123.0055226},
            {'name': "Vancity Credit Union",
                'lat': 49.266937, 'lng': -123.00630209999997}
        ]
    },

    {
        'title': 'Schools',
        'color': "#FFB81C",
        'places': [
            {
                'name': "British Columbia Institute of Technology",
                'lat': 49.25092799999999,
                'lng': -123.0034159
            },
            {
                'name': "Burnaby North Secondary School",
                'lat': 49.27801119999999,
                'lng': -122.97340810000003
            },
            {
                'name': "Brentwood Park Elementary",
                'lat': 49.2708289,
                'lng': -122.99376710000001
            },
            {
                'name': "École Alpha Secondary",
                'lat': 49.27593599999999,
                'lng': -122.99827099999999
            },
            {
                'name': "Art Institute of Vancouver Inc",
                'lat': 49.2567603,
                'lng': -122.99670320000001
            },
            {
                'name': "Kitchener Elementary School",
                'lat': 49.2725606,
                'lng': -123.01475199999999
            },
            {
                'name': "Madison Children's Centre",
                'lat': 49.2676627,
                'lng': -123.00732319999997
            },
            {
                'name': "Brentwood Preschool",
                'lat': 49.27084929999999,
                'lng': -122.99256000000003
            }
        ]
    },

    {
        'title': 'Entertainment',
        'color': "#EC028C",
        'places': [
            {
                'name': "ICBC Driver Licensing",
                'lat': 49.26521469999999,
                'lng': -123.01846749999999
            },
            {'name': "BCAA", 'lat': 49.2661273, 'lng': -123.0039418},
            {'name': "Burnaby Hospital", 'lat': 49.2497287, 'lng': -123.0160884},
            {
                'name': "Brentwood Chiropractic & Sports Rehab Centre",
                'lat': 49.274415,
                'lng': -123.01923199999999
            },
            {'name': "Dawson Medical Clinic",
                'lat': 49.2642861, 'lng': -123.0107428},
            {'name': "Dawson Dental Centre",
             'lat': 49.264352, 'lng': -123.01214620000002},
            {'name': "Canada Post", 'lat': 49.2676301, 'lng': -123.00048179999999},
            {
                'name': "Grand Villa Casino Hotel And Conference Centre",
                'lat': 49.256721,
                'lng': -123.00732199999999
            },
            {'name': "REVS", 'lat': 49.2637673, 'lng': -122.98363230000001},
            {'name': "Canlan Ice Sports", 'lat': 49.2500023,
                'lng': -122.97067500000003}
        ]
    }

]


class Command(BaseCommand):

    # @transaction.atomic
    def handle(self, *args, **options):

        instance = InteractiveGoogleMaps.objects.all().first()
        instance.place_groups.all().delete()
        
        sort_order = 0
        for category in data:            
            print(category['title'])
            
            category_instance = instance.place_groups.create(
                sort_order=sort_order,
                title = category['title'],
                color = category['color'],
            )

            sort_order += 1

            for place in category['places']:
                category_instance.places.append(
                    ('places', {                    
                            'title': place['name'],
                            'latitude': str(place['lat']),
                            'longitude': str(place['lng']),
                        }
                    )                    
                )

        instance.save()        

