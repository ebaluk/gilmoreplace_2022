import django
from django.utils import translation

if django.VERSION >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin
else:
    MiddlewareMixin = object

import re
from wthomepage.models import LanguageRootPage


class WtHomepageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.LANGUAGE_CODE = 'en-us'
        request.root_page = None
        z = re.match(r'^/([a-z]+)/.*', request.path)
        if z:
            try:
                request.root_page = LanguageRootPage.objects.get(slug=z.group(1))
            except LanguageRootPage.DoesNotExist:
                request.root_page = LanguageRootPage.objects.first()
        else:
            request.root_page = LanguageRootPage.objects.first()

        if request.root_page:
            request.LANGUAGE_CODE = request.root_page.language_code

        translation.activate(request.LANGUAGE_CODE)

