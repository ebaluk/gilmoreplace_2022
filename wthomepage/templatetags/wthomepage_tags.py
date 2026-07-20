import uuid
from django import template
register = template.Library()


@register.inclusion_tag('wthomepage/tags/hotel_contacts.html', takes_context=True)
def hotel_contacts(context):    
    request = context['request']    
    items = None    
    if request.root_page:
        items = [request.root_page]

    return {
        'items': items,
        'request': request,
    }


@register.inclusion_tag('wthomepage/tags/neighbourhood.html', takes_context=True)
def neighbourhood(context):    
    request = context['request']       
    return {        
        'request': request,
    }    


