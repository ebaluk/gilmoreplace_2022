from __future__ import absolute_import, unicode_literals

#import os


from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _
from django.views.decorators.vary import vary_on_headers

from wagtail.admin.auth import (
    PermissionPolicyChecker, permission_denied, )
from wagtail.models import Collection
from wagtail.images import get_image_model
#from wagtail.images.exceptions import InvalidFilterSpecError
#from wagtail.images.forms import URLGeneratorForm
#from wagtail.images.models import Filter
from wagtail.images.permissions import permission_policy


permission_checker = PermissionPolicyChecker(permission_policy)


from wtadmin.models import WtImageSort, WtImageSortByTag
from taggit.models import Tag, TaggedItem


@permission_checker.require_any('change')
def sort(request):  
    if request.POST:                
        if 'images[]' in request.POST.dict():
            Image = get_image_model()
            i=0
            for image_id in request.POST.getlist('images[]'):                
                image = get_object_or_404(Image, id=image_id)
                if not permission_policy.user_has_permission_for_instance(request.user, 'delete', image):
                    return permission_denied(request)        
                i+=1
                try:        
                    imgsort = WtImageSort.objects.get(image=image)
                except WtImageSort.DoesNotExist:
                    imgsort = WtImageSort(image=image)
                        
                imgsort.sort_order=i
                imgsort.save()
                
                #WtImageSort(image=image, sort_order=i).save(force_update=True)
    return HttpResponse()


@permission_checker.require_any('change')
def sort_by_tag(request, tag_id):  
    if request.POST:                
        if 'images[]' in request.POST.dict():
            tag = get_object_or_404(Tag, id=tag_id)
            Image = get_image_model()
            i=0
            for image_id in request.POST.getlist('images[]'):                
                image = get_object_or_404(Image, id=image_id)                
                if not permission_policy.user_has_permission_for_instance(request.user, 'delete', image):
                    return permission_denied(request)        
                i+=1
                try:        
                    imgsort = WtImageSortByTag.objects.get(image=image, tag=tag)
                except WtImageSortByTag.DoesNotExist:
                    imgsort = WtImageSortByTag(image=image, tag=tag)
                        
                imgsort.sort_order=i
                imgsort.save()                
                
    return HttpResponse()    

@permission_checker.require_any('add', 'change')
@vary_on_headers('X-Requested-With')
def index(request):
    #Image = get_image_model()

    # Get images (filtered by user permission)
    
    images = None

    # Filter by collection
    current_collection = None
    collection_id = request.GET.get('collection_id')
    if collection_id:
        try:
            current_collection = Collection.objects.get(id=collection_id)
            images = permission_policy.instances_user_has_any_permission_for(request.user, ['change'] )
            images = images.filter(collection=current_collection)
            images = images.extra(select={'sort_order': "SELECT sort_order FROM wtadmin_wtimagesort WHERE wtadmin_wtimagesort.image_id = wagtailimages_image.id"})
            images = images.extra(order_by = ['sort_order'])
        except (ValueError, Collection.DoesNotExist):
            pass

    collections = permission_policy.collections_user_has_any_permission_for(
        request.user, ['add', 'change']
    )
    if len(collections) < 2:
        collections = None

    # Create response    
    return render(request, 'wagtailimages/images/ordering.html', {
            'images': images,
            'query_string': None,
            'is_searching': False,

            'search_form': None,
            'popular_tags': None,
            'collections': collections,
            'current_collection': current_collection,
            'user_can_add': permission_policy.user_has_permission(request.user, 'add'),
        })



@permission_checker.require_any('add', 'change')
@vary_on_headers('X-Requested-With')
def index_tag(request):        
    images = None
    Image = get_image_model()

    # Filter by collection
    current_tag = None
    tag_id = request.GET.get('tag_id')
    if tag_id:
        try:
            current_tag = Tag.objects.get(id=tag_id)
            images = permission_policy.instances_user_has_any_permission_for(request.user, ['change'] )
            images = images.filter(tags__id=current_tag.id)
            images = images.extra(select={'sort_order': "SELECT sort_order FROM wtadmin_wtimagesortbytag WHERE wtadmin_wtimagesortbytag.image_id = wagtailimages_image.id and wtadmin_wtimagesortbytag.tag_id = {}".format(current_tag.id)})
            images = images.extra(order_by = ['sort_order'])
        except (ValueError, Tag.DoesNotExist):
            pass

    tags = Tag.objects.filter(id__in=TaggedItem.tags_for(Image).values('id'))
    if len(tags) < 2:
        tags = None

    # Create response    
    return render(request, 'wagtailimages/images/ordering_by_tag.html', {
            'images': images,
            'query_string': None,
            'is_searching': False,

            'search_form': None,
            'popular_tags': None,
            'tags': tags,
            'current_tag': current_tag,
            'user_can_add': permission_policy.user_has_permission(request.user, 'add'),
        })

