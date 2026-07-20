from django.urls import re_path
from .views import images

urlpatterns = [
    re_path(r'^admin/images/sort/', images.index, name='wtadmin_images_sort_index'),
    re_path(r'^admin/images/sort-tag/', images.index_tag, name='wtadmin_images_sort_by_tag_index'),
    re_path(r'^wtadmin/images-sort/', images.sort, name='wtadmin_images_sort'),
    re_path(r'^wtadmin/images-sort-tag/(\d+)', images.sort_by_tag, name='wtadmin_images_sort_by_tag'),    
]
