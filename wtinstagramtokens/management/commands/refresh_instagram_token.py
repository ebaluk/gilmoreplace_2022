import requests
from django.core.management.base import BaseCommand
from wtinstagramtokens.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in WtInstagramToken.objects.all():
            req = requests.get('https://graph.instagram.com/refresh_access_token',params={
                'grant_type': 'ig_refresh_token', 
                'access_token': item.token, 
            })
            data = req.json()
            if 'access_token' in data:
                item.token = data['access_token']
                item.save(force_update=True)

