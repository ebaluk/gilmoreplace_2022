from django.http import HttpResponse
from wagtail.contrib.sitemaps import views
from xml.etree import ElementTree as ET 
from .models import WtSitemap, DEFAULT_ROBOTS

def sitemap(request):
    obj = WtSitemap.for_site(request.site)
    if 'custom' == obj.type and obj.file:
        sitemap_xml = obj.file.read()
        try:
            ET.fromstring(sitemap_xml)
            response = HttpResponse(sitemap_xml)
            response['Content-Type'] = "text/xml; charset=utf-8"
            return response
        except:
            pass    
    
    return views.sitemap(request)


def robots(request):
    obj = WtSitemap.for_site(request.site)
    robots = obj.robots if obj else DEFAULT_ROBOTS 
    response = HttpResponse(robots)
    response['Content-Type'] = "text/plain; charset=utf-8"
    return response
    
