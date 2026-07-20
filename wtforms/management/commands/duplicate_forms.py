#import re
#from django.db import transaction
from django.core.management.base import BaseCommand

from wtforms.models import *


class Command(BaseCommand):
    help = 'Duplicate All Forms'
        
    
    #@transaction.atomic
    def handle(self, *args, **options):
        forms = WtForm.objects.filter(id=1)
        for form in forms:
            old_pk = form.pk 
            form.pk = None
            form.id = None
            form.name = form.name + ' - Copy' 
            form.save()
            
            old_form = WtForm.objects.get(pk=old_pk)
            
            for item in old_form.form_fields.all():
                item.page = form
                item.pk = None
                item.id = None
                item.save()
                
            # for item in old_form.emails.all():
            #     item.form = form
            #     item.pk = None
            #     item.id = None
            #     item.save()    
