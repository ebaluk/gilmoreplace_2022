from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import WtInstagramToken

class WtInstagramTokenAdmin(ModelAdmin):
    form_view_extra_css = ['wtinstagramtokens/style.css']
    model = WtInstagramToken    
    menu_icon = 'doc-full-inverse'
    list_display = ('name', )
    menu_order = 110 
    add_to_settings_menu = True

modeladmin_register(WtInstagramTokenAdmin)
