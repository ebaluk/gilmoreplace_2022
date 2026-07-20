from __future__ import absolute_import, unicode_literals
import requests

from collections import OrderedDict

import django.forms
from django.conf import settings as system_settings
from django.utils.translation import gettext_lazy as _

from wagtail.admin.forms import WagtailAdminPageForm

 
from .fields import WtFileInput, WtFileField, WtGroupField, DropDown2Field, WtSectionTitleFieldH2, WtSectionTitleFieldH3


US_STATES_CHOICES = (
        ('AK', _('Alaska')),
        ('AL', _('Alabama')),
        ('AR', _('Arkansas')),
        ('AS', _('American Samoa')),
        ('AZ', _('Arizona')),
        ('CA', _('California')),
        ('CO', _('Colorado')),
        ('CT', _('Connecticut')),
        ('DC', _('District of Columbia')),
        ('DE', _('Delaware')),
        ('FL', _('Florida')),
        ('GA', _('Georgia')),
        ('GU', _('Guam')),
        ('HI', _('Hawaii')),
        ('IA', _('Iowa')),
        ('ID', _('Idaho')),
        ('IL', _('Illinois')),
        ('IN', _('Indiana')),
        ('KS', _('Kansas')),
        ('KY', _('Kentucky')),
        ('LA', _('Louisiana')),
        ('MA', _('Massachusetts')),
        ('MD', _('Maryland')),
        ('ME', _('Maine')),
        ('MI', _('Michigan')),
        ('MN', _('Minnesota')),
        ('MO', _('Missouri')),
        ('MP', _('Northern Mariana Islands')),
        ('MS', _('Mississippi')),
        ('MT', _('Montana')),
        ('NA', _('National')),
        ('NC', _('North Carolina')),
        ('ND', _('North Dakota')),
        ('NE', _('Nebraska')),
        ('NH', _('New Hampshire')),
        ('NJ', _('New Jersey')),
        ('NM', _('New Mexico')),
        ('NV', _('Nevada')),
        ('NY', _('New York')),
        ('OH', _('Ohio')),
        ('OK', _('Oklahoma')),
        ('OR', _('Oregon')),
        ('PA', _('Pennsylvania')),
        ('PR', _('Puerto Rico')),
        ('RI', _('Rhode Island')),
        ('SC', _('South Carolina')),
        ('SD', _('South Dakota')),
        ('TN', _('Tennessee')),
        ('TX', _('Texas')),
        ('UT', _('Utah')),
        ('VA', _('Virginia')),
        ('VI', _('Virgin Islands')),
        ('VT', _('Vermont')),
        ('WA', _('Washington')),
        ('WI', _('Wisconsin')),
        ('WV', _('West Virginia')),
        ('WY', _('Wyoming')),
)


class WtBaseForm(django.forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')

        self.user = kwargs.pop('user', None)
        self.page = kwargs.pop('page', None)        
        self.enable_recaptcha = kwargs.pop('enable_recaptcha', None)
        

        super(WtBaseForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        super(WtBaseForm, self).clean()        
        
        if self.enable_recaptcha:
            recaptcha_response = self.data.get('g-recaptcha-response', None)            
            data = {
                'secret': system_settings.RECAPTCHA_SECRET,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()            

            if not result['success']:
                raise django.forms.ValidationError("reCaptcha Error")
               


class WtFormBuilder(object):
    def __init__(self, fields):
        self.fields = fields

    def create_singleline_field(self, field, options):
        # TODO: This is a default value - it may need to be changed
        options['max_length'] = 255
#         options['widget'] = django.forms.CharField.widget()
#         if field.placeholder:
#             options['widget'].attrs = {'placeholder': field.placeholder}             
        return django.forms.CharField(**options)

    def create_multiline_field(self, field, options):
        options['widget'] = django.forms.Textarea        
        return django.forms.CharField(**options)

    def create_date_field(self, field, options):        
        return django.forms.DateField(**options)

    def create_datetime_field(self, field, options):        
        return django.forms.DateTimeField(**options)

    def create_email_field(self, field, options):        
        return django.forms.EmailField(**options)

    def create_url_field(self, field, options):        
        return django.forms.URLField(**options)

    def create_number_field(self, field, options):
        return django.forms.DecimalField(**options)

    def create_dropdown_field(self, field, options):        
        options['choices'] = []           
        if field.lasso_question_list:
            if field.placeholder:
                options['choices'].append(('', field.placeholder + (' *' if field.required else '')))            
            else:
                options['choices'].append(('',''))            

            options['choices'] += [(x.lasso_id, x.title) for x in field.lasso_question_list.list_items.all()]
        else:    
            if field.placeholder:
                options['choices'].append(('', field.placeholder + (' *' if field.required else '')))            
            else:
                options['choices'].append(('',''))            
            options['choices'] += list( map(
                lambda x: (x.strip(), x.strip()),
                field.choices.splitlines()
            ) )
        return django.forms.ChoiceField(**options)

    def create_dropdown2_field(self, field, options):
        options['choices'] = [('','')] +  list( map(
            lambda x: (x.strip(), x.strip()),
            field.choices.splitlines()
        ) )
        options['choices2'] = [('','')] +  list( map(
            lambda x: (x.strip(), x.strip()),
            field.choices2.splitlines()
        ) )
        return DropDown2Field(**options)    

    def create_radio_field(self, field, options):
        if field.lasso_question_list:
            options['choices'] = [(x.lasso_id, x.title) for x in field.lasso_question_list.list_items.all()]
        else:    
            options['choices'] = map(
                lambda x: (x.strip(), x.strip()),
                field.choices.splitlines()
            )
        return django.forms.ChoiceField(widget=django.forms.RadioSelect, **options)

    def create_checkboxes_field(self, field, options):
        if field.lasso_question_list:
            options['choices'] = [(x.lasso_id, x.title) for x in field.lasso_question_list.list_items.all()]
        else:    
            options['choices'] = [(x.strip(), x.strip()) for x in field.choices.splitlines()]
        options['initial'] = [x.strip() for x in field.default_value.splitlines()]
        return django.forms.MultipleChoiceField(
            widget=django.forms.CheckboxSelectMultiple, **options
        )

    def create_checkbox_field(self, field, options):
        return django.forms.BooleanField(**options) 
    
    def create_file_field(self, field, options):
        return WtFileField(**options)
    
    def create_fields_group(self, field, options):
        return WtGroupField(**options)

    def create_section_title_h2(self, field, options):
        return WtSectionTitleFieldH2(**options)    

    def create_section_title_h3(self, field, options):
        return WtSectionTitleFieldH3(**options)        
    
    def create_state_select_field(self, field, options):
        options['choices'] =  ([(x.strip(), x.strip()) for x in field.choices.splitlines()] if field.choices else [('', _('Please Select'))]) + list(US_STATES_CHOICES)
        return django.forms.ChoiceField(**options)
    
    def create_country_select_field(self, field, options):                  
        from django_countries import countries
        options['choices'] =  ([(x.strip(), x.strip()) for x in field.choices.splitlines()] if field.choices else [('', _('Please Select'))]) + [(key, name) for key, name in countries]
        return django.forms.ChoiceField(**options)
    
    def create_time_field(self, field, options): 
        start = datetime.datetime.combine(datetime.date(1,1,1), datetime.time(0, 0, 0))        
        date_list = [start + datetime.timedelta(minutes=x) for x in range(0, 1440, 30)]        
        options['choices'] =  ( [('', '')] + [('{:%H:%M}'.format(d), '{d:%l}:{d.minute:02}{d:%p}'.format(d=d)) for d in date_list])
        return django.forms.ChoiceField(**options)
    
    def create_venue_select_field(self, field, options):                  
        from wtvenues.models import VenuePage
        options['choices'] =  ([(x.strip(), x.strip()) for x in field.choices.splitlines()] if field.choices else [('', _('Please Select'))]) + [(x.title, x.title) for x in VenuePage.objects.live()]
        return django.forms.ChoiceField(**options)

    FIELD_TYPES = {
        'singleline': create_singleline_field,
        'multiline': create_multiline_field,
        'date': create_date_field,
        'datetime': create_datetime_field,
        'email': create_email_field,
        'url': create_url_field,
        'number': create_number_field,
        'dropdown': create_dropdown_field,
        'dropdown2': create_dropdown2_field,
        'radio': create_radio_field,
        'checkboxes': create_checkboxes_field,
        'checkbox': create_checkbox_field,
        'singleline': create_singleline_field,
        
        'file' : create_file_field,
        'fieldsgroup': create_fields_group,
        'sectiontitleh2': create_section_title_h2,
        'sectiontitleh3': create_section_title_h3,
        
        'stateselect': create_state_select_field,
        'countryselect': create_country_select_field,
        'time': create_time_field,
        'venueselect': create_venue_select_field,
    }

    @property
    def formfields(self):
        formfields = OrderedDict()
        
        num = 1

        for field in self.fields:
            options = self.get_field_options(field)

            if field.field_type in self.FIELD_TYPES:
                formfields[field.clean_name] = self.FIELD_TYPES[field.field_type](self, field, options)
                formfields[field.clean_name].show_label = field.show_label
                formfields[field.clean_name].pk = field.pk
                formfields[field.clean_name].add_css_class = field.add_css_class
                formfields[field.clean_name].clean_related_input_name = field.clean_related_input_name                
                formfields[field.clean_name].clean_name_2 = field.clean_name_2
                formfields[field.clean_name].num = num
                formfields[field.clean_name].field_type = field.field_type
                num += 1
                
                if field.placeholder:
                    placeholder = field.placeholder
                    if field.required:
                        placeholder = placeholder + ' *'

                    formfields[field.clean_name].widget.attrs['placeholder'] = placeholder
                                
            else:
                raise Exception("Unrecognised field type: " + field.field_type)

        formfields['guid'] = django.forms.CharField(required=False, widget=django.forms.HiddenInput(attrs={'id': ''}))
        
        return formfields

    def get_field_options(self, field):
        options = {}
        options['label'] = field.label
        options['help_text'] = field.help_text
        options['required'] = field.required
        options['initial'] = field.default_value
        #options['attrs'] = {'placeholder': field.placeholder}         
        #formfields[field.clean_name].placeholder = field.placeholder
                
        return options

    def get_form_class(self):
        return type(str('WagtailForm'), (WtBaseForm,), self.formfields)


class SelectDateForm(django.forms.Form):
    date_from = django.forms.DateTimeField(
        required=False,
        widget=django.forms.DateInput(attrs={'placeholder': 'Date from'})
    )
    date_to = django.forms.DateTimeField(
        required=False,
        widget=django.forms.DateInput(attrs={'placeholder': 'Date to'})
    )


class WagtailAdminWtFormPageForm(WagtailAdminPageForm):

    def clean(self):

        super(WagtailAdminWtFormPageForm, self).clean()

        # Check for dupe form field labels - fixes #585
        if 'form_fields' in self.formsets:
            _forms = self.formsets['form_fields'].forms
            for f in _forms:
                f.is_valid()

            for i, form in enumerate(_forms):
                if 'label' in form.changed_data:
                    label = form.cleaned_data.get('label')
                    for idx, ff in enumerate(_forms):
                        # Exclude self
                        if idx != i and label == ff.cleaned_data.get('label'):
                            form.add_error(
                                'label',
                                django.forms.ValidationError(_('There is another field with the label %s, please change one of them.' % label))
                            )
