from django.urls import re_path
from .views import inlinepanelsorter_image

urlpatterns = [    
    re_path(r'^wtadmin/inlinepanelsorter/get-image/(?P<image_id>\d+)/$', inlinepanelsorter_image, name='inlinepanelsorter_image'),
]
