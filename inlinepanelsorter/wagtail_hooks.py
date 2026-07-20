from django.utils.html import format_html, format_html_join
from wagtail import hooks
from django.conf import settings

@hooks.register('insert_editor_css')
def editor_css():
    return format_html('<link rel="stylesheet" href="' + settings.STATIC_URL + 'inlinepanelsorter/css/admin.css?4">')
 

@hooks.register('insert_editor_js')
def editor_js():
    js_files = [        
        'inlinepanelsorter/js/admin.js',
        'vendors/js/Sortable.min.js',        
    ]
    return format_html_join('\n', '<script src="{0}{1}?2"></script>', ((settings.STATIC_URL, filename) for filename in js_files))
    