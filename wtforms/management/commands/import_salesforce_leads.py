import os
import re
import requests
#from django.db import transaction
from django.core.management.base import BaseCommand

from wtforms.models import *


class Command(BaseCommand):
    help = 'Import Salesforce Leads'
    
    def handle(self, *args, **options):
        leads = []
        p = re.compile(r'^([0-9a-zA-Z]+)[\s]+=[\s]+(.*)')
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'leads.txt') 

        with open(data_file, 'r') as f:
            lines = f.readlines()           
            lead = {}
            for line in lines:
                if line.startswith('00N1U00000U19AE'):
                    lead = {}
                matches = p.match(line)
                if matches:
                    lead[matches.group(1)] = matches.group(2)

                if line.startswith('state'):
                    leads.append(lead)


        for lead in leads:
            r = requests.post('https://webto.salesforce.com/servlet/servlet.WebToLead?encoding=UTF-8', data=lead )
            
        



        