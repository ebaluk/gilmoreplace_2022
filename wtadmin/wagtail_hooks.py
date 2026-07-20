# -*- coding: utf-8 -*-
from django.utils.html import format_html, format_html_join

from wagtail import hooks
from django.conf import settings

@hooks.register('insert_editor_css')
def editor_css():
  return format_html('<link rel="stylesheet" href="' + settings.STATIC_URL + 'wtadmin/css/admin.css">')
  #return format_html('<link rel="stylesheet" href="' + settings.STATIC_URL + 'vendors/font-awesome/css/font-awesome.min.css">')

def allow_all_attributes(tag):
    pass

def whitelister_element_rules():
    #,"DOCTYPE","fieldset","form","head","html","meta","body"
    tags=["a","abbr","acronym","address","area","b","base","bdo","big","blockquote","br","button","caption","cite","code","col","colgroup", 
    "dd","del","dfn","div","dl","dt","em","h1","h2","h3","h4","h5","h6","hr","i","img","input","ins","kbd","label","legend","li","link",
    "map","noscript","object","ol","optgroup","option","p","param","pre","q","samp","script","select","small","span","strong","sub","sup",
    "table","tbody","td","textarea","tfoot","th","thead","title","tr","tt","ul","var"]
    return dict((tag, allow_all_attributes) for tag in tags)

hooks.register('construct_whitelister_element_rules', whitelister_element_rules)

# def editor_js():
#     js_files = [
#         'vendors/js/jquery.htmlClean.min.js',
#         #'wtadmin/js/hallo-justify.js',
#         #'wtadmin/js/images-delete.js',
#         'vendors/rangy/rangy-core.js',
#         'vendors/rangy/rangy-selectionsaverestore.js',
#     ]
#     js_includes = format_html_join('\n', '<script src="{0}{1}"></script>', ((settings.STATIC_URL, filename) for filename in js_files))
#     # return js_includes + (
#     #     """
#     #     <script>
#     #     registerHalloPlugin('hallojustify1');
#     #     registerHalloPlugin('hallohtml');
#     #     registerHalloPlugin('hallocleanhtml');
#     #     </script>
#     #     """
#     # )

# hooks.register('insert_editor_js', editor_js)

@hooks.register('insert_global_admin_js')
def global_admin_js():
    js_files = [
        #'wtadmin/js/images-delete.js',
        'vendors/tinyColorPicker/colors.js',
        'vendors/tinyColorPicker/jqColorPicker.min.js',                
    ]
    js_includes = format_html_join('\n', '<script src="{0}{1}"></script>', ((settings.STATIC_URL, filename) for filename in js_files)) 
    return js_includes + (
        """
        <script>
        $(function(){
            $('.colorPicker').colorPicker({opacity: false, forceAlpha: false});
        });
        </script>
        """
    )
