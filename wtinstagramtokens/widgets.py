from django.forms import widgets
from django.utils.safestring import mark_safe

class WtInstagramTokenProfilePhotoWidget(widgets.HiddenInput):

    def render(self, name, value, attrs=None):
        ret = super(WtInstagramTokenProfilePhotoWidget, self).render(name, value, attrs)
        if value:
            ret += mark_safe('<img src="'+value+'">')
        return ret    
            
            
