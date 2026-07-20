from wagtail import hooks
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import Tower, TowerPage, TowerBedroomTypes, TowerPlanFloorPlateImageRendition


class TowerAdmin(ModelAdmin):
    model = Tower
    menu_label = 'Towers'
    menu_icon = 'doc-full'
    list_display = ('title', )
    search_fields = ('title', )
    menu_order = 432
    add_to_settings_menu = False
        
modeladmin_register(TowerAdmin)


class TowerBedroomTypesAdmin(ModelAdmin):
    model = TowerBedroomTypes
    menu_label = 'Tower Bedroom Types'
    menu_icon = 'doc-full'
    list_display = ('title', 'sort_order')
    search_fields = ('title', )
    menu_order = 432
    add_to_settings_menu = True
        
modeladmin_register(TowerBedroomTypesAdmin)

# class TowerPlanFloorPlateImageRenditionAdmin(ModelAdmin):
#     model = TowerPlanFloorPlateImageRendition
#     menu_label = 'Floor Plate Renditions'
#     menu_icon = 'doc-full'
#     list_display = ('tower_plan', 'image_hash')    
#     menu_order = 432
#     add_to_settings_menu = True
        
# modeladmin_register(TowerPlanFloorPlateImageRenditionAdmin)



# @hooks.register('before_serve_page')
# def tower_params_helper(page, request, serve_args, serve_kwargs):
#     request.tower_page = None
#     if isinstance(page, TowerPage):
#         request.tower_page = page.specific        
#     else:
#         request.tower_page = TowerPage.objects.ancestor_of(page).live().first()
        
    



