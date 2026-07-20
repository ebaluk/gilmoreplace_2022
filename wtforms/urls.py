from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from wtforms import views

urlpatterns = [
    #re_path(r'^$', views.index, name='index'),
    re_path(r'^submissions/(\d+)/$', views.list_submissions, name='list_submissions'),
    re_path(r'^submissions/(\d+)/(\d+)/delete/$', views.delete_submission, name='delete_submission')
]
app_name='wtforms'
