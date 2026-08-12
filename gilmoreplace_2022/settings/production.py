# -*- coding: utf-8 -*-
from .base import *  # noqa: F403
from .base import _validate_nextjs_urls
import os

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False

_allowed = os.environ.get("ALLOWED_HOSTS", "").strip()
if not _allowed or _allowed == "*":
    raise ValueError(
        "ALLOWED_HOSTS must be set to an explicit comma-separated list "
        "(do not use '*' in production)."
    )
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()]

SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
if not SECRET_KEY or SECRET_KEY in ("change-me-in-production", "change-me"):
    raise ValueError("SECRET_KEY must be set to a strong random value in production.")

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
# HTTPS is terminated at host nginx-proxy; containers talk HTTP internally.
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "0") in ("1", "true", "True")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in _csrf_origins.split(",") if origin.strip()
    ]

# Internal Docker hostname for server→Next revalidate (not for browsers).
NEXTJS_BASE_URL = os.environ.get("NEXTJS_BASE_URL", "http://frontend:3000")


def _resolve_nextjs_public_url():
    """
    Browser-facing origin for Wagtail preview / catch-all redirects.

    Never fall back to NEXTJS_BASE_URL — that is often http://frontend:3000
    inside Compose and breaks admin preview links in the browser.
    """
    explicit = (os.environ.get("NEXTJS_PUBLIC_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit

    virtual_host = (os.environ.get("VIRTUAL_HOST") or "").strip().split(",")[0].strip()
    if virtual_host:
        return f"https://{virtual_host}"

    csrf = globals().get("CSRF_TRUSTED_ORIGINS") or []
    if csrf:
        return str(csrf[0]).rstrip("/")

    raise ValueError(
        "NEXTJS_PUBLIC_URL (or VIRTUAL_HOST / CSRF_TRUSTED_ORIGINS) must be set "
        "for production preview and redirects."
    )


NEXTJS_PUBLIC_URL = _resolve_nextjs_public_url()
REVALIDATION_SECRET = os.environ.get("REVALIDATION_SECRET", "").strip()
_weak_secrets = (
    "change-me-in-production",
    "change-me",
    "replace-with-long-random",
    "replace-with-other-long-random",
)
if not REVALIDATION_SECRET or REVALIDATION_SECRET in _weak_secrets:
    raise ValueError("REVALIDATION_SECRET must be set to a strong random value in production.")

PREVIEW_SECRET = os.environ.get("PREVIEW_SECRET", "").strip()
if not PREVIEW_SECRET or PREVIEW_SECRET in _weak_secrets or PREVIEW_SECRET == "change-me-preview":
    raise ValueError(
        "PREVIEW_SECRET must be set to a strong random value in production "
        "(do not reuse REVALIDATION_SECRET)."
    )
if PREVIEW_SECRET == REVALIDATION_SECRET:
    raise ValueError("PREVIEW_SECRET must be distinct from REVALIDATION_SECRET.")

WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {
        "default": NEXTJS_PUBLIC_URL.rstrip("/"),
    },
    "SERVE_BASE_URL": NEXTJS_PUBLIC_URL.rstrip("/"),
    "REDIRECT_ON_PREVIEW": True,
    "ENFORCE_TRAILING_SLASH": False,
}

_validate_nextjs_urls(NEXTJS_PUBLIC_URL)

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
