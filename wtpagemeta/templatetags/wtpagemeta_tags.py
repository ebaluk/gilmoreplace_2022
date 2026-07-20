import re
from django import template
from wtpagemeta.models import WtPageMeta
register = template.Library()

@register.inclusion_tag('wtpagemeta/tags/base.html', takes_context=True)
def page_meta(context, page):
    image = None
    title = None
    description = None
    keywords = None
    fb_app_id = None
    site_name = None
    
    o = WtPageMeta.objects.first()    
    
    if page:
        
        if hasattr(page, 'get_meta_fields'):
            title, description, keywords, image = getattr(page, 'get_meta_fields')
        else:     
            title = page.specific.seo_title if page.specific.seo_title else page.specific.title                                  
            description = page.specific.search_description
            keywords = page.specific.seo_keywords      
            try:
                image = page.specific.open_graph_image
            except:
                pass
        
    if o:
        fb_app_id = o.fb_app_id
        site_name = o.site_name
        if not image:          
            image = o.default_image
        if not title:          
            title = o.default_title
        if not description:          
            description = o.default_description            
        if not keywords:          
            keywords = o.default_keywords           
            
    if description:          
        description = re.sub(r'[\n\r]+', ' ', description, flags=re.MULTILINE)             
    if keywords:          
        keywords = re.sub(r'[\n\r]+', ' ', keywords, flags=re.MULTILINE)        
            

    return {        
        'page': page,
        'request': context['request'],
        'url': context['request'].build_absolute_uri(),
        'title': title,
        'description': description,
        'keywords': keywords,
        'image': image,
        'site_name': site_name,
        'fb_app_id': fb_app_id,
    }
