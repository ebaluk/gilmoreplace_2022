from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import InteractiveGoogleMaps





class InteractiveGoogleMapsAdmin(ModelAdmin):
    model = InteractiveGoogleMaps
    menu_label = 'Neighborhood Map'
    menu_icon = 'doc-full'
    list_display = ('title', )
    search_fields = ('title', )
    menu_order = 431
    add_to_settings_menu = False
        
modeladmin_register(InteractiveGoogleMapsAdmin)


