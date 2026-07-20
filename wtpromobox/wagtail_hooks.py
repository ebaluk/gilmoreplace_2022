from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import *

class PromoBoxItemAdmin(ModelAdmin):
    model = PromoBoxItem
    menu_label = 'Promo Boxes'
    #menu_icon = 'doc-full-inverse'
    menu_icon = 'date'
    list_display = ('title','visible',)    
    search_fields = ('title')
    menu_order = 110 
    add_to_settings_menu = False

#class MyModelAdminGroup(ModelAdminGroup):
    #menu_label = 'Caption'
    #menu_icon = 'folder-open-inverse' 
    #menu_order = 200 
    #items = (NetCityAdmin,)


#wagtailmodeladmin_register(MyModelAdminGroup)
modeladmin_register(PromoBoxItemAdmin)
