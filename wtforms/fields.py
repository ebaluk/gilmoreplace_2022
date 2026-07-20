from django.forms.fields import CharField, FileField, MultiValueField, ChoiceField 
from django.forms.widgets import MultiWidget, FileInput, HiddenInput, Select
from django.core.exceptions import ValidationError 

class DropDown2Widget(MultiWidget):
    def __init__(self, widgets, attrs=None):        
        
        # widgets = (            
        #     Select,
        #     Select,
        # )
        super(DropDown2Widget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return [None, None]

class DropDown2Field(MultiValueField):
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.get('choices')
        choices2 = kwargs.get('choices2')
        
        fields = (
            ChoiceField(choices=choices),
            ChoiceField(choices=choices2),
        ) 

        
        self.widget = DropDown2Widget(widgets=[Select(choices=choices), Select(choices=choices2)])

        if 'choices' in kwargs:
            del kwargs['choices']
        if 'choices2' in kwargs:
            del kwargs['choices2']


        
        super(DropDown2Field, self).__init__(*args, fields=fields, require_all_fields=True, **kwargs)        

    def compress(self, data_list):
        if data_list:
            return ", " .join(data_list)
        return None         

class WtFileInput(MultiWidget):
    def __init__(self, attrs=None):
        
        widgets = (            
            FileInput(attrs),
            HiddenInput(attrs),
        )
        super(WtFileInput, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split(',')
        return [None, None]
    
    
class WtFileField(MultiValueField):
    def __init__(self, *args, **kwargs):
        
        fields = (
            FileField(),
            CharField(initial='no'),
        )
        
        kwargs['widget'] = kwargs.pop('widget', WtFileInput())
        super(WtFileField, self).__init__(fields=fields, require_all_fields=False, *args, **kwargs)        


    def clean(self, value):
        clean_data = []
        errors = []
        if not value or isinstance(value, (list, tuple)):
            if not value or not [v for v in value if v not in self.empty_values]:
                if self.required:
                    raise ValidationError(self.error_messages['required'], code='required')
                else:
                    return self.compress([])
        else:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        
        field = self.fields[0]
        
        try:
            field_value = value[0]
        except IndexError:
            field_value = None
            
        if field_value in self.empty_values:
            if field.required:
                if field.error_messages['incomplete'] not in errors:
                    errors.append(field.error_messages['incomplete'])
        else:        
            try:
                clean_data.append(field.clean(field_value))
            except ValidationError as e:                
                errors.extend(m for m in e.error_list if m not in errors)
                if errors:
                    raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def compress(self, data_list):
        if data_list:
            return data_list[0]
        return None 


    
class WtGroupField(CharField):
    is_form_group = True
    add_css_class = ''
    show_label = True
    def __init__(self, *args, add_css_class=None, show_label=True, **kwargs):
        self.add_css_class = add_css_class
        self.show_label = show_label
        super(WtGroupField, self).__init__(*args, **kwargs)
            

class WtSectionTitleFieldH2(CharField):
    is_section_title_h2 = True
    add_css_class = ''
    show_label = True
    def __init__(self, *args, add_css_class=None, show_label=True, **kwargs):
        self.add_css_class = add_css_class
        self.show_label = show_label
        super(WtSectionTitleFieldH2, self).__init__(*args, **kwargs)

class WtSectionTitleFieldH3(CharField):
    is_section_title_h3 = True
    add_css_class = ''
    show_label = True
    def __init__(self, *args, add_css_class=None, show_label=True, **kwargs):
        self.add_css_class = add_css_class
        self.show_label = show_label
        super(WtSectionTitleFieldH3, self).__init__(*args, **kwargs)        

        
            
