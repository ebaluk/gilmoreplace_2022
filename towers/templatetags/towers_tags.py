import uuid
from collections import OrderedDict
from django import template
from towers.models import Tower, TowerPage
register = template.Library()

def _get_tower(page):
    ret = None
    if page:
        if isinstance(page.specific, TowerPage):
            ret = page.specific
        else:
            ret = TowerPage.objects.ancestor_of(page).live().first()
    return ret    


@register.inclusion_tag('towers/tags/plans_widget.html', takes_context=True)
def tower_plans_widget(context, title=None, title_2=None, page=None):
    request = context['request']
    tower_page = _get_tower(page)
    if tower_page and tower_page.tower_type:
        apartment_types = {}
        for plan in tower_page.tower_type.plans.exclude(bedrooms__visible=False):
            if not plan.bedrooms.id in apartment_types:
                apartment_types[plan.bedrooms.id] = {
                    'title': plan.bedrooms.title, 
                    'title_zh_hans': plan.bedrooms.title_zh_hans,
                    'title_zh_hant': plan.bedrooms.title_zh_hant,
                    'sort_order': plan.bedrooms.sort_order,
                    'apartments': [],
                }                
            apartment_types[plan.bedrooms.id]['apartments'].append(plan)
    
        return {
            'apartment_types': OrderedDict(sorted(apartment_types.items(), key=lambda t: t[1]['sort_order'])),
            'title': title,
            'title_2': title_2,
            'request': context['request'],
        }    

@register.inclusion_tag('towers/tags/views_widget.html', takes_context=True)
def tower_views_widget(context, title=None, title_2=None, text=None, page=None, penthouses_only=False):
    request = context['request']
    towers = []
    items = []
    tower_page = _get_tower(page)
    if tower_page and tower_page.tower_type:
        _views = tower_page.tower_type.views.all()
        if penthouses_only:
            _views = _views.filter(penthouse_view=True)  
        _views = _views.order_by('-sort_order')

        for item in _views:
            items.append({
                'title': item.title, 
                'image': item.image,
            })
    else:
        _towers = Tower.objects.all().order_by('id')        
        for tower in _towers:
            items = []
            _views = tower.views.all()
            if penthouses_only:
                _views = _views.filter(penthouse_view=True)  
            _views = _views.order_by('-sort_order')
            for item in _views:
                items.append({
                    'title': item.title, 
                    'image': item.image,
                })
            towers.append({
                'title': tower,
                'items': items,
            })    

    
    return {
        'items': items,
        'towers': towers,
        'title': title,
        'title_2': title_2,
        'text': text,
        'request': request,
    }    


@register.inclusion_tag('towers/tags/penthouses_widget.html', takes_context=True)
def penthouses_widget(context, title=None, title_2=None, text=None):
    penthouse_types = {}
    towers = []
    _towers = Tower.objects.all().order_by('id')
    for tower in _towers:
        plans = tower.plans.exclude(penthouse_type__isnull=True)
        towers.append({
            'id': tower.id,
            'title': tower.title,
            'plans': plans,
        })
        for plan in plans:
            if not plan.penthouse_type.id in penthouse_types:
                penthouse_types[plan.penthouse_type.id] = plan.penthouse_type
    
    return {
        'penthouse_types': OrderedDict(sorted(penthouse_types.items(), key=lambda t: t[1].sort_order)),
        'towers': towers,
        'title': title,
        'title_2': title_2,
        'text': text,
        'request': context['request'],
    }
