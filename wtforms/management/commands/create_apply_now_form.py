import os
import re
import requests
#from django.db import transaction
from django.core.management.base import BaseCommand

from wtforms.models import *

shared_fields = [
    {
        'label': '1. About You',
        'required': False,
        'field_type': 'fieldsgroup',
    },
    {
        'label': 'Step 1 - Applicant Information',
        'required': False,
        'field_type': 'sectiontitleh2',                
    },
    {
        'label': 'First Name',
        'placeholder': '',
        'show_label': True,
        'help_text': '',
        'required': True,
        'field_type': 'singleline',
        'choices': '',        
        'default_value': '',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': None,
        'lasso_field_name': 'firstName',        
    },
    {
        'label': 'Last Name',
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'lastName',        
    },
    {
        'label': 'Email',
        'field_type': 'email',                
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'email',        
    },
    {
        'label': 'Telephone',
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'phone',        
    },
    {
        'label': 'Street Address',
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'address',        
    },
    {
        'label': 'City',
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6 other-select',
        'related_input_class': 'city-other-input',
        'lasso_field_name': 'city',        
        'choices': ['Burnaby', 'Colwood', 'Coquitlam', 'Delta', 'Langford', 'Langley', 'Maple Ridge', 'Nanaimo', 'New Westminster', 'North Vancouver', 'Pitt Meadows', 'Port Coquitlam', 'Port Moody ', 'Richmond', 'Sooke', 'Squamish', 'Surrey', 'Sidney', 'Vancouver', 'Victoria', 'View Royal', 'West Vancouver ', 'Whistler', 'White Rock', 'Other',]                        
    },    
    {
        'label': 'city-other-input',
        'field_type': 'singleline',
    },
    {
        'label': 'Province',
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'state',        
    },
    {
        'label': 'Postal',
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',                        
        'lasso_field_name': 'zipCode',        
    },
    {
        'label': 'How did you hear about us?',
        'required': True,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 106044, 
        
    },
    {
        'label': '2. Your Home',
        'required': False,
        'field_type': 'fieldsgroup',
    },
    {
        'label': "Step 2 - Prospective Tenant's Information",
        'required': False,
        'field_type': 'sectiontitleh2',                
    },    
    {
        'label': 'Unit Type',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': {'coldwood': '129191', 'port_moody': '129192'},
    },
    {
        'label': 'Monthly Rent',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120990,
    },
    {
        'label': 'Move in Month',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120991,
    },
    {
        'label': 'Move in Date',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120992,
    },
    {
        'label': 'Need parking?',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120993,
    },
    {
        'label': 'Need a storage Locker?',
        'required': False,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120994,
    },
    
    {
        'label': '3. Your References',
        'required': False,
        'field_type': 'fieldsgroup',
    },
    {
        'label': "Step 3 - Financial & References",
        'required': False,
        'field_type': 'sectiontitleh2',                
    },


    {
        'label': 'Employment Status',
        'required': True,
        'field_type': 'dropdown',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120995,
    },

    {
        'label': "Applicant Details",
        'required': False,
        'field_type': 'sectiontitleh3',                
    },    
    {
        'label': 'Current Employer',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120996,
    },
    {
        'label': 'Employer Address',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120997,
    },
    {
        'label': 'Current Position',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120998,
    },
    {
        'label': 'Length of Employment',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 120999,
    },
    {
        'label': 'Supervisor Name',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121000,
    },
    {
        'label': 'Supervisor Telephone',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121001,
    },
    {
        'label': 'Total Gross Annual Income',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121002,
    },
    {
        'label': 'Landlord Name',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121004,
    },
    {
        'label': 'Landlord Phone Number',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121005,
    },
    
    {
        'label': "Personal References: (One relative only)",
        'required': False,
        'field_type': 'sectiontitleh3',                
    },
    {
        'label': 'Personal Reference Name #1',
        'required': True,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121006,
    },
    {
        'label': 'Personal Reference Phone #1',
        'required': True,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121007,
    },
    {
        'label': 'Personal Reference Relationship #1',
        'required': True,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',
        'lasso_question_list': 121008,
    },

    {
        'label': "Personal References #2",
        'required': False,
        'add_css_class': 'personal-reference-2',
        'field_type': 'sectiontitleh3',
    },
    
    {
        'label': 'Personal Reference Name #2',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6 hr-above',        
        'lasso_question_list': 121009,
    },
    {
        'label': 'Personal Reference Phone #2',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121010,
    },
    {
        'label': 'Personal Reference Relationship #2',
        'required': False,
        'field_type': 'singleline',
        'add_css_class': 'col-sm-6',        
        'lasso_question_list': 121011,
    },
                            
    {
        'label': '4. Your Consent',
        'required': False,
        'field_type': 'fieldsgroup',
    },
    {
        'label': "Step 4 - Statement & Consent",
        'required': False,
        'field_type': 'sectiontitleh2',                
    },
    {
        'label': 'Live A Comment',
        'required': False,
        'field_type': 'multiline',
        'add_css_class': 'col-sm-12',        
        'lasso_field_name': 'Comment',
    },
    {
        'label': 'I consent to receiving commercial electronic messages, including messages about upcoming developments, special incentives, events, and market updates from Onni Marketing Inc. on behalf of the current and future members of the Onni Group. I acknowledge I can withdraw my consent at any time by unsubscribing as set out below.',
        'required': True,
        'field_type': 'checkbox',
        'add_css_class': 'col-sm-12',                        
        'lasso_question_list': 121015,
    },

]


locations = [
    {                
        'name': 'Lasso Apply Now Form Coldwood',
        'uid': 'coldwood',
        'lasso_uid': '334kd5#Ank',           
        'lasso_client_id': '1273',
        'lasso_project_id': '14235',
        'lasso_source_type': 'Online Registration',
        'lasso_secondary_source_type': 'coldwood',
        'lasso_follow_up_process_id': '52383',
        'lasso_domain_account_id': 'LAS-128832-10',

        'hidden_fields': [
            {'thankYouEmailTemplateId': '774201'},
            {'rotationId': '320273'},
        ]                   
        
    },
    {
        'name': 'Lasso Apply Now Form Port Moody',
        'uid': 'port_moody',
        'lasso_uid': '334kd5#Ank',           
        'lasso_client_id': '1273',
        'lasso_project_id': '14235',
        'lasso_source_type': 'Online Registration',
        'lasso_secondary_source_type': 'coldwood',
        'lasso_follow_up_process_id': '52384',
        'lasso_domain_account_id': 'LAS-128832-10',

        'hidden_fields': [
            {'thankYouEmailTemplateId': '777092'},
            {'rotationId': '320272'},                    
        ]                   
        
    },
]

class Command(BaseCommand):
    help = 'Create Apply Now Form'

    def _get_list(self, lasso_id):
        lasso_id=str(lasso_id)
        print('Question List: ', lasso_id)
        
        ret = WtFormLassoList.objects.get(lasso_id=lasso_id)
        # except WtFormLassoList.DoesNotExist:
        #     question = questions[lasso_id]  
        #     print('Question List: ', lasso_id)                      
        #     ret = WtFormLassoList(
        #         title='{} - {}'.format(lasso_id, question['title']),
        #         lasso_id=lasso_id,                
        #         field_type=question['field_type'],
        #     )
        #     if 'answers' in question:
        #         sort_order = 0
        #         for item in question['answers']:
        #             for k, v in item.items():                     
        #                 print(k, v)
        #                 ret.list_items.create(
        #                     sort_order=sort_order,
        #                     lasso_id=k,
        #                     title=v,                        
        #                 )
        #                 sort_order += 1
        #     ret.save()
        return ret

    
    def handle(self, *args, **options):
        
        return
        
        for loc in locations:
            # p = re.compile(r'^([0-9a-zA-Z]+)[\s]+=[\s]+(.*)')
            name = loc['name']
            print('Location: ', name)

            values = {
                'name': name,
                'post_to_lasso': True,
                'lasso_api_url': 'https://api.lassocrm.com/v1/registrants',
                'lasso_api_key': 'eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjcyMjY1ODI0MDAsInRva2VuRGF0YSI6IntcbiAgXCJwcm9qZWN0SWRcIiA6IDE3NTgyLFxuICBcImNsaWVudElkXCIgOiAxMjczLFxuICBcIm5hbWVcIiA6IFwibGFzc29SZWdpc3RyYXRpb25cIlxufSIsImlzcyI6Ikxhc3NvVG9rZW4iLCJhdWQiOiJMYXNzbyIsInRva2VuSWQiOjMyMTQyfQ.azkTXt1HT73jq6Ef2SWigJdgIG7MxJt3EIaglMT0wCIhYcZ1gfHsGIIvUbkDz1AwdGiRVtcZMZA2ThOFv0n2GK2a6SE6pLh6Xiu3hnNLZjtT7ppdXwaV7lJ_7_JO6-4Nmzmhensv15x3F6GAgUdgxbDhg_pCWAMLvLU0fu1JR02462HWJpd0eG8aXsTkccNs7jot5BgXlCpQfok0rZzjEgr-bvMAaa-grmpPKsN4Jp03cn5nws07PP9Z04E7t8FHOEj_xVojjZ_RL0HJvAL-eg5TKF0MumQmDQ0VLW-PTpeawuDGUMYtSuW7gKSw2psPTBJNbvCbsK4AaIAAqSDdPg',

                'lasso_uid': loc['lasso_uid'],
                'lasso_client_id': loc['lasso_client_id'],
                'lasso_project_id': loc['lasso_project_id'],
                
                'lasso_domain_account_id': loc['lasso_domain_account_id'],
                'lasso_source_type': loc['lasso_source_type'],
                'lasso_secondary_source_type': loc['lasso_secondary_source_type'],
                'lasso_follow_up_process_id': loc['lasso_follow_up_process_id'],
            }

            try:
                form = WtForm.objects.get(name=name)                
            except WtForm.DoesNotExist:            
                form = WtForm()

            for k, v in values.items():
                    setattr(form, k, v)    

            form.hidden_fields.all().delete()        
            form.form_fields.all().delete()

            sort_order = 0

            for field in shared_fields:

                item = form.form_fields.create(
                    sort_order=sort_order,
                    label=field['label'],                   
                )

                sort_order += 1

                if 'placeholder' in field:
                    item.placeholder = field['placeholder']
                
                if 'show_label' in field:
                    item.show_label = field['show_label']

                if 'help_text' in field:
                    item.help_text = field['help_text']       

                if 'required' in field:
                    item.required = field['required']

                if 'field_type' in field:
                    item.field_type = field['field_type']    

                if 'choices' in field:
                    item.choices = '\n'.join(field['choices'])

                if 'default_value' in field:
                    item.default_value = field['default_value']            

                if 'add_css_class' in field:
                    item.add_css_class = field['add_css_class']

                if 'related_input_class' in field:
                    item.related_input_class = field['related_input_class']    
                

                if 'lasso_question_list' in field:
                    if isinstance(field['lasso_question_list'], dict):
                        item.lasso_question_list = self._get_list(field['lasso_question_list'][loc['uid']])
                    elif field['lasso_question_list']:                     
                        item.lasso_question_list =  self._get_list(field['lasso_question_list'])

                if 'lasso_field_name' in field:
                    item.lasso_field_name =  field['lasso_field_name']
        
            sort_order = 0                
            for field in loc['hidden_fields']:                
                for k, v in field.items():    
                    form.hidden_fields.create(
                        sort_order=sort_order,
                        name=k,
                        value=v,
                    )
                sort_order += 1

            
            

            form.save()
            