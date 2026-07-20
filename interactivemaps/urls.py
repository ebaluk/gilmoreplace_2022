from django.urls import re_path
from .views import layout_image

urlpatterns = [    
    re_path(r'^wtadmin/interactivemaps/get-image/(?P<image_id>\d+)/$', layout_image, name='wtadmin_interactivemaps_layout_image'),
]
