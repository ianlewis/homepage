# Django settings for homepage project.

import os
import sys
import posixpath

from homepage.conf import env_var, email_csv, csv_list

ROOT_PATH = os.path.dirname(__file__)

DEBUG = env_var('DEBUG', bool, default=False)
TEMPLATE_DEBUG = env_var('TEMPLATE_DEBUG', bool, default=DEBUG)

ADMINS = env_var('ADMINS', email_csv, default=())
MANAGERS = env_var('MANAGERS', email_csv, default=ADMINS)

_db_engine = env_var('DB_ENGINE', default='sqlite3' if DEBUG else 'mysql')
if _db_engine == 'sqlite3':
    _db_name = env_var('DB_NAME', default='djangodb.sqlite')
else:
    _db_name = env_var('DB_NAME', default="homepage")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % _db_engine,
        'NAME': _db_name,
        'USER': env_var('DB_USER', default=''),
        'PASSWORD': env_var('DB_PASSWORD', default=''),
        'HOST': env_var('DB_HOST', default=''),
        'PORT': env_var('DB_PORT', default=''),
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = env_var('TIME_ZONE', default='Asia/Tokyo')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env_var('LANGUAGE_CODE', default='en-us')

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
SITE_MEDIA_ROOT = os.path.join(ROOT_PATH, 'site_media')
MEDIA_ROOT = env_var('MEDIA_ROOT',
                     default=os.path.join(SITE_MEDIA_ROOT, 'media'))
STATIC_ROOT = env_var('STATIC_ROOT',
                      default=os.path.join(SITE_MEDIA_ROOT, 'static'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
SITE_MEDIA_URL = '/'
MEDIA_URL = posixpath.join(SITE_MEDIA_URL, 'media/')
STATIC_URL = posixpath.join(SITE_MEDIA_URL, 'static/')

STATICFILES_DIRS = (
    os.path.join(ROOT_PATH, 'static'),
)

STATICFILES_MEDIA_DIRNAMES = (
    'media',
    'static',
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "homepage.core.finders.AppMediaDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

COMPRESS_ENABLED = env_var('COMPRESS_ENABLED', default=not DEBUG)
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

# Make this unique, and don't share it with anybody.
if not DEBUG:
    # NOTE: Secret key is required in debug mode.
    SECRET_KEY = env_var('SECRET_KEY')
else:
    SECRET_KEY = env_var('SECRET_KEY', default='snake-oil')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

if not DEBUG:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    'django.contrib.messages.context_processors.messages',
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "homepage.core.context_processors.debug",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

USE_X_FORWARDED_HOST = True

# Setup page caching.
# TODO: Use nginx or varnish?
USE_PAGE_CACHE = env_var('USE_PAGE_CACHE', bool, default=not DEBUG)
if USE_PAGE_CACHE:
    MIDDLEWARE_CLASSES = (
        'homepage.core.middleware.GoogleAnalyticsStripCookieMiddleware',
        'django.middleware.cache.UpdateCacheMiddleware',
    ) + MIDDLEWARE_CLASSES + (
        'django.middleware.cache.FetchFromCacheMiddleware',
    )

    CACHE_MIDDLEWARE_ALIAS = 'page_cache'


USE_MEMCACHED = env_var('USE_MEMCACHED', bool, default=not DEBUG)
if USE_MEMCACHED:
    _cache_backend = 'django.core.cache.backends.memcached.PyLibMCCache'
    _cache_location = env_var('MEMCACHED_HOSTS', csv_list,
                              default=['127.0.0.1:11211'])
else:
    # NOTE: Default is local memory cache.
    _cache_backend = 'django.core.cache.backends.locmem.LocMemCache'
    _cache_location = ''  # Not used by LocMemCache

CACHES = {
    'default': {
        'BACKEND': _cache_backend,
        'LOCATION': _cache_location,
    },
    'page_cache': {
        'BACKEND': _cache_backend,
        'LOCATION': _cache_location,
        'KEY_PREFIX': 'page_cache1',
        'TIMEOUT': 600,
    },
    'compress': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 2000,
    }
}
COMPRESS_CACHE_BACKEND = 'compress'


ROOT_URLCONF = 'homepage.urls'

TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',

    # Third party
    'compressor',
    'south',
    'sorl.thumbnail',
    'pagination',
    'tagging',
    'disqus',

    # app
    'homepage.core',
    'homepage.blog',
)

# Need this to get around a bugs in HttpResponseRedirect
# for non-ascii urls and flatpages
APPEND_SLASH = False

# django-tagging
FORCE_LOWERCASE_TAGS = True

# django-pagination
PAGINATION_DEFAULT_PAGINATION = 9
PAGINATION_INVALID_PAGE_RAISES_404 = True
PAGINATION_DEFAULT_WINDOW = 3

# django-disqus
DISQUS_API_KEY = env_var('DISQUS_API_KEY', default='')
DISQUS_WEBSITE_SHORTNAME = env_var('DISQUS_WEBSITE_SHORTNAME', default='')

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(name)s] %(levelname)s %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'stderr': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
        },
        'stdout': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django.request': {
            'handlers': ['stderr'],
            'propagate': False,
            'level': 'ERROR',
        },
    }
}

INTERNAL_IPS = env_var('INTERNAL_IPS', csv_list, default=())

SOUTH_MIGRATION_MODULES = {
    "blog": "homepage.migrations.blog",
    "tagging": "homepage.migrations.tagging",
    "thumbnail": "homepage.migrations.thumbnail",
}
