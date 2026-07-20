import os
import re
import requests
#from django.db import transaction
from django.core.management.base import BaseCommand
from wtforms.models import *

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        api_key = 'eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjcyMjY1ODI0MDAsInRva2VuRGF0YSI6IntcbiAgXCJwcm9qZWN0SWRcIiA6IDMyOTUsXG4gIFwiY2xpZW50SWRcIiA6IDE0OSxcbiAgXCJuYW1lXCIgOiBcImxhc3NvUmVnaXN0cmF0aW9uXCJcbn0iLCJpc3MiOiJMYXNzb1Rva2VuIiwiYXVkIjoiTGFzc28iLCJ0b2tlbklkIjo0ODcxfQ.GXGu9AQam7cDusqmqdkPwI2N78EhkGiEG8ctp5M90zgdCZuLi0tZLL8h_clW_G483yr9vtjwUNNojfMijMziLIKLFEM_p53Pl4RDmBoY_pyZB9J_EvdyWfS0OZfef3slYFMNSZHYt81Fh_KwdPej4z3RtX8I2pnQQNlG2U40OobD20c3IdFdaMvNKo2pXpACo_pnsdhuEMxCKhhceB9PO7gKnGe6SsBpSvEEP6Z9jUuH0bvY0KjYtbqFOllW5WwyjqLoYCtYmv-rxVHdCK88RFhGLBKWyI7USaVFa2VCruLauhdBl4TGazxn411SnR5PD8cRbR7ZCMyRAVZ5UZ86qQ'
        r = requests.get(
            'https://api.lassocrm.com/v1/projects/settings', 
            headers={"Authorization": "Bearer %s" % api_key},
        )        
        data = r.json()

        for question in data['questions']:            
            lasso_id = question['questionId']
            title = question['name']
            #title='{} - {}'.format(lasso_id, name)            
            
            print(title)
            try:
                lasso_instance = WtFormLassoList.objects.get(lasso_id=question['questionId'])
                if lasso_instance.title != title:
                    lasso_instance.title = title
                    lasso_instance.save()
                lasso_instance.list_items.all().delete()    
            except WtFormLassoList.DoesNotExist:                
                lasso_instance = WtFormLassoList(
                    title=title,
                    lasso_id=lasso_id,                
                    field_type=question['type'],
                )


            

            if 'answers' in question:
                sort_order = 0
                for answer in question['answers']:
                    answerId = answer['answerId']
                    answerTitle = answer['answer']
                    print(answerId, answerTitle)
                    lasso_instance.list_items.create(
                        sort_order=sort_order,
                        lasso_id=answerId,
                        title=answerTitle,                        
                    )
                    sort_order += 1
            
            lasso_instance.save()

                