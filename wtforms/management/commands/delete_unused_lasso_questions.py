import os
import re
import requests
#from django.db import transaction
from django.core.management.base import BaseCommand

from wtforms.models import *


class Command(BaseCommand):

    
    def handle(self, *args, **options):

        questions = WtFormLassoList.objects.all()
        for question in questions:
            fields = WtFormField.objects.filter(lasso_question_list=question)
            if not fields:
                question.delete()

        