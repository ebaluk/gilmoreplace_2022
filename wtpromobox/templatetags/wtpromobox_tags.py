from django import template
from wtpromobox.models import PromoBoxItem
register = template.Library()

@register.inclusion_tag('wtpromobox/promobox.html', takes_context=True)
def promo_box(context, page):
    if page:        
        
        items = PromoBoxItem.objects.filter(visible=True, pages__page=page)
        if items:
            return {
                'id': page.pk,        
                'page': page,
                'request': context['request'],
                'self': items.first(),            
            }

