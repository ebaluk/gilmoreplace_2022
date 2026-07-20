# -*- coding: utf-8 -*-
from .base import *
import os

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "gilmoreplace_2022"),
        "USER": os.environ.get("DB_USER", "django"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

CSRF_COOKIE_DOMAIN = os.environ.get("CSRF_COOKIE_DOMAIN", None) or None

CORS_ALLOWED_ORIGINS = (
    os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
)

# Behind nginx-proxy (HTTPS termination on host)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in _csrf_origins.split(",") if origin.strip()
    ]

# Host for Next.js frontend (revalidation webhook / public preview URL)
NEXTJS_BASE_URL = os.environ.get("NEXTJS_BASE_URL", "http://localhost:3000")
NEXTJS_PUBLIC_URL = os.environ.get("NEXTJS_PUBLIC_URL", NEXTJS_BASE_URL)
REVALIDATION_SECRET = os.environ.get("REVALIDATION_SECRET", "change-me-in-production")
PREVIEW_SECRET = os.environ.get("PREVIEW_SECRET", "") or REVALIDATION_SECRET

WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": NEXTJS_PUBLIC_URL.rstrip("/"),
    },
    "SERVE_BASE_URL": NEXTJS_PUBLIC_URL.rstrip("/"),
    "REDIRECT_ON_PREVIEW": True,
    "ENFORCE_TRAILING_SLASH": False,
}

REDIS_URL = os.environ.get("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": True},
    },
}
