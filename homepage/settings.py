# Django settings for homepage project.

import os
import sys
import posixpath

from homepage.conf import env_var, email_csv, csv_list

ROOT_PATH = os.path.dirname(__file__)

DEBUG = env_var("DEBUG", bool, default=False)
TESTING = env_var("TESTING", bool, default=DEBUG)

ADMINS = env_var("ADMINS", email_csv, default=())
MANAGERS = env_var("MANAGERS", email_csv, default=ADMINS)

# Address of the BLOG grpc service.
BLOG_ADDRESS = env_var("BLOG_ADDRESS", default="blog:50051")

_db_engine = env_var("DB_ENGINE", default="sqlite3" if DEBUG else "mysql")
_db_name = env_var("DB_NAME", default="homepage")
_db_timeout = env_var("DB_TIMEOUT", int, default=3)
_db_options = {"connect_timeout": _db_timeout}
if _db_engine == "sqlite3":
    _db_name = env_var("DB_NAME", default="djangodb.sqlite")
    _db_options = {"timeout": _db_timeout}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.%s" % _db_engine,
        "NAME": _db_name,
        "USER": env_var("DB_USER", default=""),
        "PASSWORD": env_var("DB_PASSWORD", default=""),
        "HOST": env_var("DB_HOST", default=""),
        "PORT": env_var("DB_PORT", default=""),
        "OPTIONS": _db_options,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = env_var("TIME_ZONE", default="Asia/Tokyo")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env_var("LANGUAGE_CODE", default="en-us")

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
SITE_MEDIA_ROOT = os.path.join(ROOT_PATH, "site_media")
MEDIA_ROOT = env_var("MEDIA_ROOT", default=os.path.join(SITE_MEDIA_ROOT, "media"))
STATIC_ROOT = env_var("STATIC_ROOT", default=os.path.join(SITE_MEDIA_ROOT, "static"))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
SITE_MEDIA_URL = "/admin/"
MEDIA_URL = posixpath.join(SITE_MEDIA_URL, "media/")
STATIC_URL = posixpath.join(SITE_MEDIA_URL, "static/")

STATICFILES_DIRS = (os.path.join(ROOT_PATH, "static"),)

STATICFILES_MEDIA_DIRNAMES = ("media", "static")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
if not DEBUG:
    # NOTE: Secret key is required in debug mode.
    SECRET_KEY = env_var("SECRET_KEY")
else:
    SECRET_KEY = env_var("SECRET_KEY", default="snake-oil")

# Set session and csrf cookies so they are only sent over a secure connection.
SESSION_COOKIE_SECURE = env_var("USE_HTTPS", bool, default=not DEBUG)
CSRF_COOKIE_SECURE = env_var("USE_HTTPS", bool, default=not DEBUG)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (os.path.join(ROOT_PATH, "templates"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": env_var("TEMPLATE_DEBUG", bool, default=DEBUG),
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
            ],
        },
    }
]

MIDDLEWARE_CLASSES = ["homepage.health.middleware.HealthCheckMiddleware"]

MIDDLEWARE_CLASSES += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # TODO: Transaction handling
    # 'django.middleware.transaction.TransactionMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
]

USE_X_FORWARDED_HOST = True

# USE_MEMCACHED = env_var('USE_MEMCACHED', bool, default=not DEBUG)
# if USE_MEMCACHED:
#     _cache_backend = 'django.core.cache.backends.memcached.PyLibMCCache'
#     _cache_location = env_var('MEMCACHED_HOSTS', csv_list,
#                               default=['127.0.0.1:11211'])
# else:
#     # NOTE: Default is local memory cache.
#     _cache_backend = 'django.core.cache.backends.locmem.LocMemCache'
#     _cache_location = ''  # Not used by LocMemCache

FILEBASED_CACHE_PATH = env_var("FILEBASED_CACHE_PATH", default="")
USE_FILEBASED_CACHE = FILEBASED_CACHE_PATH != ""
if USE_FILEBASED_CACHE:
    _cache_backend = "django.core.cache.backends.filebased.FileBasedCache"
    _cache_location = FILEBASED_CACHE_PATH
else:
    # NOTE: Default is local memory cache.
    _cache_backend = "django.core.cache.backends.locmem.LocMemCache"
    _cache_location = ""  # Not used by LocMemCache

CACHES = {
    "default": {"BACKEND": _cache_backend, "LOCATION": _cache_location},
}

ROOT_URLCONF = "homepage.urls"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.staticfiles",
    # app
    "homepage.core",
    "homepage.blog",
    "homepage.events",
]

# Need this to get around a bugs in HttpResponseRedirect
# for non-ascii urls and flatpages
APPEND_SLASH = False

# logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {"null": {"level": "DEBUG", "class": "logging.NullHandler"}},
    "loggers": {"": {"handlers": ["null"]}},
}
if env_var("ENABLE_LOGGING", bool, default=True):
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s][%(name)s] %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "stderr": {
                "level": "ERROR",
                "formatter": "verbose",
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
            },
            "stdout": {
                "level": "DEBUG",
                "formatter": "verbose",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["stdout"],
                "level": env_var("LOG_LEVEL", default="DEBUG" if DEBUG else "INFO"),
            },
            "django.request": {
                "handlers": ["stderr"],
                "propagate": False,
                "level": "ERROR",
            },
        },
    }

INTERNAL_IPS = env_var("INTERNAL_IPS", csv_list, default=())

# Allow any subdomain of ianlewis.org
_allowed_hosts = [".ianlewis.org", ".ianlewis.org."]
if DEBUG:
    _allowed_hosts = ["*"]
ALLOWED_HOSTS = env_var("ALLOWED_HOSTS", csv_list, default=_allowed_hosts)
