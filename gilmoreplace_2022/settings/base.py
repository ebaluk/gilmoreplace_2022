import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


INSTALLED_APPS = [
    'wtpages',
    'wtadmin',
    'wtforms',
    'wthomepage',
    'wtfavicon',
    'wtinstagramtokens',
    'interactivemaps',
    'interactivegooglemaps',
    'towers',

    'wtpagemeta',
    'wtsitemap',

    'imagefilters',

    'wtpromobox',
    'inlinepanelsorter',

    'wagtail.contrib.sitemaps',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'wagtail.contrib.settings',

    'wagtail_modeladmin',
    'wagtail_headless_preview',

    'modelcluster',
    'taggit',

    'wagtailvideos',
    'wagtailvideos_autoencode',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'wagtail.api.v2',

]


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Gilmore Place Headless API',
    'DESCRIPTION': 'Wagtail headless endpoints consumed by the Next.js frontend.',
    'VERSION': '1.0.0',
}

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # 'django.middleware.csrf.CsrfViewMiddleware',
    'wtforms.models.DisableCSRF',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.contrib.legacy.sitemiddleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)


ROOT_URLCONF = 'gilmoreplace_2022.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'gilmoreplace_2022.wsgi.application'


JAVASCRIPT_FILES = {}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGES = (
    ('en-us', "English"),
    ("zh-hant", "Traditional Chinese"),
    ("zh-hans", "Simplified Chinese"),
)

LANGUAGES_TRANSLATIONS = {
    'en-us': "EN",
    "zh-hans": "简",
    "zh-hant": "繁",
}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]


TIME_ZONE = 'America/Vancouver'

USE_I18N = True

USE_L10N = True

USE_TZ = True
# USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')
MEDIA_URL = '/media_files/'

UPLOADS_ROOT = os.path.join(MEDIA_ROOT, 'uploads')
UPLOADS_URL = '/media_files/uploads/'


WAGTAIL_ENABLE_UPDATE_CHECK = False

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    # 'handlers': {
    # 'mail_admins': {
    # 'level': 'ERROR',
    # 'filters': ['require_debug_false'],
    # 'class': 'django.utils.log.AdminEmailHandler'
    # }
    # },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': os.path.join(PROJECT_DIR, '../log/debug.log'),
        },
    },
    'loggers': {
        'django': {
            # 'handlers': ['mail_admins','file'],
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# Wagtail settings
WAGTAIL_SITE_NAME = "Gilmore Place"
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Browser-facing Next.js origin (admin preview + catch-all redirects).
# Server-to-server revalidate uses NEXTJS_BASE_URL (may be Docker hostname).
NEXTJS_PUBLIC_URL = os.environ.get("NEXTJS_PUBLIC_URL", "http://localhost:3000")
NEXTJS_BASE_URL = os.environ.get("NEXTJS_BASE_URL", NEXTJS_PUBLIC_URL)
REVALIDATION_SECRET = os.environ.get("REVALIDATION_SECRET", "")
# Shared secret for draft preview API (Next → Django). Falls back to revalidation secret.
PREVIEW_SECRET = os.environ.get("PREVIEW_SECRET", "") or REVALIDATION_SECRET

WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": NEXTJS_PUBLIC_URL.rstrip("/"),
    },
    "SERVE_BASE_URL": NEXTJS_PUBLIC_URL.rstrip("/"),
    "REDIRECT_ON_PREVIEW": True,
    "ENFORCE_TRAILING_SLASH": False,
}


def _validate_nextjs_urls(public_url=None):
    """Warn when browser-facing preview URL looks like an internal Docker hostname."""
    import warnings

    public = (public_url if public_url is not None else NEXTJS_PUBLIC_URL) or ""
    public = public.rstrip("/")
    internal_markers = ("://frontend", "://backend", "://nginx")
    if any(m in public for m in internal_markers):
        warnings.warn(
            "NEXTJS_PUBLIC_URL=%r looks like an internal Docker hostname; "
            "browsers cannot open Wagtail preview links. "
            "Use a public origin (e.g. http://localhost:3000 or https://your.domain)."
            % public,
            UserWarning,
            stacklevel=2,
        )


_validate_nextjs_urls()


# CORS configuration for headless frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True



SOC_TW_CONSUMER_KEY = os.environ.get('SOC_TW_CONSUMER_KEY', '0hnCvg3OiWXhcOSPVA2w3w')
SOC_TW_CONSUMER_SECRET = os.environ.get('SOC_TW_CONSUMER_SECRET', 'fa4T3DtK70yx5kGd3wNIG4djQP0z3UbieGQq7f83Sc')
SOC_TW_USER_TOKEN = os.environ.get('SOC_TW_USER_TOKEN', '976477442-CyPrigfUPlJo92awxeghit3UlTDlSLeS9UcVmnGr')
SOC_TW_USER_SECRET = os.environ.get('SOC_TW_USER_SECRET', 'PlDV5gvY01BlI1BnuJC8iAdztJdXNwxE51lLs2y44')

SOC_IN_ACCESS_TOKEN = os.environ.get('SOC_IN_ACCESS_TOKEN', '294023234.ab103e5.b74cadadb1554917a679de870fdf1f44')

SOC_FB_APP_ID = os.environ.get('SOC_FB_APP_ID', "158866010930199")
SOC_FB_APP_SECRET = os.environ.get('SOC_FB_APP_SECRET', '0f4f51403cd6cbdcae2590c36059267c')

MAIN_MENU_TYPE = 'logo-left'
MAIN_MENU_AFFIX = True

RECAPTCHA_SITEKEY = os.environ.get('RECAPTCHA_SITEKEY', '6LcTW10UAAAAAODX0vJJkPy7ijRn3LqkE0rvo1FI')
RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET', '6LcTW10UAAAAACXRP1P0FdOZrDMCevNdF6hlyjCd')

GOOGLE_MAP_API_KEY = os.environ.get('GOOGLE_MAP_API_KEY', 'AIzaSyBT3agucwzH4RQvZ0QQEOCzY44P4t9uAFM')


# WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Silence treebeard.E001 — Wagtail's PageManager/CollectionManager intentionally
# do not subclass MP_NodeManager. This is a forward-compat notice for Treebeard 6.
SILENCED_SYSTEM_CHECKS = ["treebeard.E001"]

# MAILCHIMP_KEY = '25ad156e8341eafc8b4e2992deeea71c-us20'
# MAILCHIMP_USER = 'epoehlman@altamareagroup.com'
# MAILCHIMP_LIST_ID = '58d416bed9'


def GA_VIEW_ID():
    from wtadmin.models import WtSettings
    o = WtSettings.objects.first()
    if o:
        return 'ga:{}'.format(o.ga_view_id)
    else:
        return 'ga:55933424'
