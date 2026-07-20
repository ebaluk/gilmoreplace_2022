from django.urls import re_path
from .views import sitemap, robots

urlpatterns = [
    re_path(r'^sitemap\.xml$', sitemap),
    re_path(r'^robots\.txt$', robots),    
]
