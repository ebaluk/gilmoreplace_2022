import uuid
from django import template
register = template.Library()


@register.inclusion_tag('interactivemaps/tags/interactive_map.html', takes_context=True)
def interactive_map(context, instance=None, show_legend=False):    
    if instance:        
        return {
            'map': instance,
            'uid': 'interactive-map-layout-%s' % str(uuid.uuid4()),
            'show_legend': show_legend,
            'request': context['request'],
        }    

