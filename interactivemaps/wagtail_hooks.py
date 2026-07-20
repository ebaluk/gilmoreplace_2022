from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from .models import InteractiveMaps

from django.utils.html import format_html, format_html_join
from wagtail import hooks
from django.conf import settings

@hooks.register('insert_global_admin_css')
def editor_css():
    return format_html('<link rel="stylesheet" href="' + settings.STATIC_URL + 'interactivemaps/css/admin.css?4">')


@hooks.register('insert_global_admin_js')
def editor_js():
    js_files = [
        'interactivemaps/js/admin.js',
    ]
    return format_html_join('\n', '<script src="{0}{1}?2"></script>', ((settings.STATIC_URL, filename) for filename in js_files))




class InteractiveMapsAdmin(ModelAdmin):
    model = InteractiveMaps
    menu_label = 'Interactive Maps'
    menu_icon = 'doc-full'
    list_display = ('title', )
    search_fields = ('title', )
    menu_order = 431
    add_to_settings_menu = False
        
modeladmin_register(InteractiveMapsAdmin)


