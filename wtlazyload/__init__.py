from django.conf import settings
settings.JAVASCRIPT_FILES['vendors/blazy/polyfills/closest.js'] = 1
settings.JAVASCRIPT_FILES['vendors/blazy/blazy.js'] = 1
 
settings.MIDDLEWARE = settings.MIDDLEWARE + ('wtlazyload.middleware.LazyLoadMiddleware',)
