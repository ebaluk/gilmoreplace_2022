from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from wagtail.images import get_image_model

@never_cache
def layout_image(request, image_id=None):
    if not request.user.has_perm('wagtailadmin.access_admin'):
        return JsonResponse({})
    
    data = {}

    Image = get_image_model()
    
    try:
        image = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        image = None
     
    data['modal'] = render_to_string('interactivemaps/admin/layout_image_editor.html', {'image': image})      

    return JsonResponse(data)
