from pathlib import Path
from datetime import timedelta

from decouple import config


# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="127.0.0.1"
)


# =========================================================
# APPLICATIONS
# =========================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "jazzmin",
    "debug_toolbar",
    "drf_spectacular",
    "rest_framework",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.waiter",
    "apps.orders",
    "apps.admin_panel",
    "apps.chef",
    "apps.cashier",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================================================
# CACHES
# =========================================================

CACHES = {
    'default': {},
    'cache-for-ratelimiting': {},
}
RATELIMIT_USE_CACHE = 'cache-for-ratelimiting'
RATELIMIT_VIEW = "apps.accounts.views.ratelimit_error" 
# =========================================================
# URLS & WSGI
# =========================================================

ROOT_URLCONF = 'parvoz.urls'

WSGI_APPLICATION = "parvoz.wsgi.application"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    'default': {
        'ENGINE': config("DB_ENGINE", default="django.db.backends.sqlite3"),
        'NAME': config("DB_NAME"),   
        'USER': config("DB_USER"),   
        'PASSWORD': config("DB_PASSWORD"),  
        'HOST': config("DB_HOST", default="127.0.0.1"),
        'PORT': config("DB_PORT")
    }
}


# =========================================================
# AUTH PASSWORD VALIDATORS
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC & MEDIA FILES
# =========================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# DJANGO DEFAULTS
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/auth/access-denied/"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}


# =========================================================
# SIMPLE JWT
# =========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
}


# =========================================================
# DRF SPECTACULAR
# =========================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Parvoz API",
    "DESCRIPTION": "Restaurant & Cafe System",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,
}


# =========================================================
# DEBUG TOOLBAR
# =========================================================

INTERNAL_IPS = [
    "127.0.0.1",
]