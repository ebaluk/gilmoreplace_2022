import json
import uuid
#from django.db import transaction
from django.core.management.base import BaseCommand

from wtpages.models import *


class Command(BaseCommand):
    help = 'Convert Related Links'
        
    
    #@transaction.atomic
    def handle(self, *args, **options):
        pages = Page.objects.all().specific()
        for page in pages:
            flg = False
            if hasattr(page, 'stream_field'):                 
                for block in page.stream_field.stream_data:
                    if 'paragraph' == block['type']:                    
                        if 'links' in block['value'] and len(block['value']['links']):
                            if not flg:
                                print(page, page.pk)
                            flg = True
                            for link in block['value']['links']:
                                print(link)

                                if 'new_links' in block['value']:
                                    block['value']['new_links']['links'] = []
                                else:
                                    block['value']['new_links'] = {
                                        'align': 'text-left',
                                        'links': [],
                                    } 
                                
                                block['value']['new_links']['links'].append(
                                    {                                
                                        'link_type': link['value']['link_type'], 
                                        'title': link['value']['title'], 
                                        'new_window': link['value']['new_window'], 
                                        'link_page': link['value']['link_page'], 
                                        'link_doc': link['value']['link_doc'], 
                                        'link_external': link['value']['link_external'], 
                                    }
                                )

                        del block['value']['links']        

                if flg:
                    
                    page.save()
                                
