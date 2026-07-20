from django.urls import re_path
from .views import preview404 

urlpatterns = [
    re_path(r'^404.html$', preview404),        
]
