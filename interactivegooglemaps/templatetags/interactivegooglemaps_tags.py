import uuid
from django import template
register = template.Library()


@register.inclusion_tag('interactivegooglemaps/tags/places_widget.html', takes_context=True)
def places_widget(context, instance=None):
    if instance:        
        return {
            'self': instance,
            'uid': 'places-widget-%s' % str(uuid.uuid4()),            
            'request': context['request'],
        }    

