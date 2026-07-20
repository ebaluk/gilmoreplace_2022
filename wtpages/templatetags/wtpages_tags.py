import re
import os
import datetime
import uuid

from django.template.loader import render_to_string
from datetime import date
from django import template
from django.conf import settings
from django.utils import translation
from django.utils.safestring import mark_safe
from django.db.models import Q

from wtpages.models import *

from django.conf import settings as system_settings
import logging
logger = logging.getLogger('django')

register = template.Library()


@register.simple_tag(takes_context=True)
def pageurl(context, page):        
    return page.specific.relative_url(context['request'].site)


@register.simple_tag()
def debug_object_dump(var):
    try:
        return vars(var)
    except:
        return 'Something wrong in debug_object_dump'

@register.simple_tag(takes_context=True)
def get_request_meta(context):
    return context['request'].META
    

@register.simple_tag(takes_context=True)
def get_form_inline(context, form):
    ff = form.get_form()
    return {
        'form': ff,
        'request': context['request'],
    }

@register.simple_tag
def get_all_static_files():
    ret = {'css': [], 'js': [],}    
    
    globaljs = getattr(system_settings, 'JAVASCRIPT_FILES', None)
    if globaljs:       
        for js in globaljs:
            ret['js'].append(mark_safe(js))
            
    
    for app in system_settings.INSTALLED_APPS:
        fl = os.path.join('js', '%s.js' %  app )  
        if os.path.exists(os.path.join(system_settings.BASE_DIR, app, "static", fl)):
            ret['js'].append(mark_safe(fl))            
            
        fl = os.path.join('css', '%s.css' %  app )  
        if os.path.exists(os.path.join(system_settings.BASE_DIR, app, "static", fl)):
            ret['css'].append({'t': mark_safe('text/css'), 'f':mark_safe(fl)})
            
        fl = os.path.join('css', '%s.scss' %  app )  
        if os.path.exists(os.path.join(system_settings.BASE_DIR, app, "static", fl)):
            ret['css'].append({'t': mark_safe('text/x-scss'), 'f':mark_safe(fl)})    
                
    return ret                 
       
@register.simple_tag
def get_system_settings():                    
    return settings                 

@register.simple_tag
def get_wtadmin(): 
    from wtadmin.models import WtSettings                   
    return WtSettings.objects.first()


@register.simple_tag(takes_context=True)
def get_site_lang(context, self):
    return 'en'
    

def has_menu_children(page):
    return page.get_children().live().in_menu().exists()

@register.inclusion_tag('wtpages/tags/top_menu.html', takes_context=True)
def top_menu(context, calling_page=None):

    
    root_page = context['request'].root_page
    menuitems = root_page.get_children().specific().live().in_menu()
    
    active_page = None
    cnt = len(menuitems)
    for menuitem in menuitems:      
        menuitem.active = calling_page.url.startswith(menuitem.url) if calling_page else False    
        if menuitem.active:
            active_page = menuitem


        try:
            if menuitem.link:
                menuitem.link = menuitem.link
                menuitem.external = menuitem.external
        except AttributeError:
            pass

    return {        
        'calling_page': calling_page,
        'request': context['request'],
        'items': menuitems,
        'active_page': active_page,
        'itemcount': cnt,
    }

@register.inclusion_tag('wtpages/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent, calling_page=None):
    menuitems = None
    if parent:
        menuitems = parent.get_children().specific().live().in_menu()
        if menuitems:
            for menuitem in menuitems:                

                try:
                    if menuitem.link:
                        menuitem.link = menuitem.link
                        menuitem.external = menuitem.external
                except AttributeError:
                    pass
                
                menuitem.active = calling_page.url.startswith(menuitem.url) if calling_page else False

        return {
            'calling_page': calling_page,
            'parent': parent,
            'items': menuitems,
            'request': context['request'],            
        }


@register.inclusion_tag('wtpages/tags/page_navbar.html', takes_context=True)
def page_navbar(context, page=None):        
    if page:
        menuitems = None
        request = context['request']        
        if page.show_navbar:
            menuitems = page.get_children().in_menu().live().specific()
        else:    
            p = page.get_parent().specific
            if hasattr(p, 'show_navbar') and p.show_navbar:
                menuitems = p.get_children().in_menu().live().specific()
        
        if menuitems:
            for menuitem in menuitems:            
                if page and page.url.startswith(menuitem.url):
                    menuitem.active = True                    

            return {
                'menuitems': menuitems,
                'request': request,
                'page': page,
            }    
    
   
    
@register.inclusion_tag('wtpages/includes/carousel.html', takes_context=True)
def carousel(context, carousel_items, lazy_load=True, fallback_items=False, show_controls=False, carousel_style='fading', imagesize='', carousel_class='slideshow', interval=5000, ignore_visible=False, gallery_mode=False, carousel_items_mobile=None, imagesize_mobile='' ):
    items = carousel_items if carousel_items else fallback_items
    id = uuid.uuid4()    
    carousel_responsive_class_desktop = ''
    carousel_responsive_class_mobile = ''
    if carousel_items_mobile:
        carousel_responsive_class_desktop = 'hidden-xs'
        carousel_responsive_class_mobile = 'visible-xs-block'

    return {
        'id_desktop': 'carousel-desktop-%s' % id,
        'id_mobile': 'carousel-mobile-%s' % id,
        'show_controls': show_controls,
        'carousel_style': carousel_style,
        'carousel_items': items,  
        'imagesize': imagesize,
        'carousel_class': carousel_class,
        'interval': interval,
        'ignore_visible': ignore_visible,
        'lazy_load': lazy_load,
        'gallery_mode': gallery_mode,
        'carousel_items_mobile': carousel_items_mobile,
        'imagesize_mobile': imagesize_mobile,
        'carousel_responsive_class_desktop': carousel_responsive_class_desktop,
        'carousel_responsive_class_mobile': carousel_responsive_class_mobile,
        'request': context['request'],
    }   

@register.filter
def to_class_name(value):
    return value.__class__.__name__.lower()


def get_rendered_theme(obj):
    res = '';
    try:
        if obj.theme.id:
            th = '.themed-'+ type(obj).__name__ + '-'+ str(obj.id)
            th = th.lower()
            if obj.theme.color:
                res += th+' *{color: '+obj.theme.color+"}\n"
            if obj.theme.background:
                res += th+'{background-color: '+obj.theme.background+"}\n"
            if obj.theme.title_color:
                res += th+' h1,'+th+' h2,'+th+' h3,'+th+' h4{color: '+obj.theme.title_color+"}\n"
            if obj.theme.title_background:
                res += th+' h1,'+th+' h2,'+th+' h3,'+th+' h4{color: '+obj.theme.title_color+"}\n"

            if obj.theme.css:
                css = obj.theme.css
                p = re.compile( "\{theme\}")
                res += p.sub( th, css)
    except:
        pass

    return res


@register.simple_tag(takes_context=True)
def render_all_themes(context):
    ret = ''    
    for obj in CssTheme.objects.all():         
        ret += obj.render_theme()
    
    ret = mark_safe(ret)    
        
    return ret




@register.simple_tag(takes_context=True)
def jscode(context, pos, page=None):
    jsc = ''
    items = JsCode.objects.filter(doc_position=pos)
    if page:
        items = items.filter(Q(pages__page=page) | Q(pages__page__isnull=True))
        items = items.exclude(exclude_pages__page=page)    
    for code in items:
        jsc += code.text
    if jsc:
        return mark_safe(jsc)
    return ''

@register.simple_tag(takes_context=True)
def youtube_code(context, link):
    #'<iframe width="" height="" src="https://www.youtube.com/embed/'.@$matches[1].'" frameborder="0" allowfullscreen></iframe>';
    # https://www.youtube.com/watch?v=B_8y-lmm08E
    return 'https://www.youtube.com/embed/' + link.replace('https://www.youtube.com/watch?v=','')


@register.inclusion_tag('wtpages/tags/address.html', takes_context=True)
def address(context, show_email=False, show_more_info=False, show_logo=False, show_get_map=False, phone_html_class='', show_hours=False):
    request = context['request']
    if request.root_page:
        return {
            'address': request.root_page,
            'show_email': show_email,
            'show_more_info': show_more_info,
            'show_logo': show_logo,
            'show_get_map': show_get_map,
            'phone_html_class': phone_html_class,
            'show_hours': show_hours,
            'request': request,
        }    

@register.simple_tag()
def tomorrow(delta):
    nextday = datetime.date.today() + datetime.timedelta(days=delta)
    return nextday.strftime('%m/%d/%Y')

def get_top_navbar_pages(request, parent_page=None, inline=False):
    ret = []

    if not parent_page:
        parent_page = request.root_page

    pages = parent_page.get_children().live()
    #.in_menu()
    for page in pages:
        page = page.specific
        if getattr(page, 'show_in_sitemap', True):
            flg = False
    
            is_url_page = 'URLPage' == page.__class__.__name__
            is_form_link_page = 'FormLinkPage' == page.__class__.__name__

            item = {'title': page.title, 'url': '', 'inline': flg, 'subpages': get_top_navbar_pages(request, parent_page=page, inline=flg) , }
    
            try:
                if is_url_page:
                    item['url'] = page.__dict__.get('link', None)
                    item['target'] = '_blank' if page.external else '_self'
                elif is_form_link_page:
                    item['url'] = '#'
                    item['cls'] = 'wtform-modal-link'
                    item['wtform_id'] = page.form.pk
                elif inline:
                    if page.show_in_menus:
                        item['url'] = '%s#%s' % ( parent_page.relative_url(request.site, request), page.slug )
                    else:
                        continue
                else:
                    item['url'] = page.relative_url(request.site, request)
    
            except:
                pass

            ret.append(item)

    return ret


@register.inclusion_tag('wtpages/tags/site_map.html', takes_context=True)
def site_map(context):
    request = context['request']
    return {
        'sitemap': get_top_navbar_pages(request),
        'request': request,
    }
            
@register.simple_tag()
def animation_delay(time=0.13, idx=0):    
    return time * idx

