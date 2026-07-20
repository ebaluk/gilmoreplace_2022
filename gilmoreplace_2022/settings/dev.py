import os

from .base import *

DEBUG = True
ALLOWED_HOSTS=['*']
LOGGING = {}
#TEMPLATE_DEBUG = True

#TEMPLATES['OPTIONS']['debug'] = 'DEBUG';
TEMPLATES[0]['OPTIONS']['debug'] = True

COMPRESS_ENABLED = False

SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

#SECRET_KEY = 'a)jc_j=q0l5=!ibo!_=4^u$-w+!chf+&xe3vu$@a1mus#fnpmd'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS.append('wagtail.contrib.styleguide')


ENABLE_SHOP = True

#INSTALLED_APPS.append('wtlazyload')



DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "gilmoreplace_2022"),
        "USER": os.environ.get("DB_USER", "django"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "123"),
        "HOST": os.environ.get("DB_HOST", "postgres"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

if not os.environ.get("DISABLE_LOCAL_SETTINGS"):
    try:
        from .local import *  # noqa: F401,F403
    except ImportError:
        pass
