# Django settings for homepage project.

import os
import sys
import posixpath

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_PATH = os.path.dirname(__file__)
PROJECT_PATH = os.path.dirname(ROOT_PATH)

ADMINS = (
    #('', ''),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'djangodb.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'ianlewis_hp',
#        'USER': 'root',
#        'PASSWORD': '',
#        'HOST': '',
#        'PORT': '',
#    }
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Tokyo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
SITE_MEDIA_ROOT = os.path.join(PROJECT_PATH, 'site_media')
MEDIA_ROOT = os.path.join(SITE_MEDIA_ROOT, 'media')
STATIC_ROOT = os.path.join(SITE_MEDIA_ROOT, 'static')
FILEBROWSER_DIRECTORY = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
SITE_MEDIA_URL = '/'
MEDIA_URL = posixpath.join(SITE_MEDIA_URL, 'media/')
STATIC_URL = posixpath.join(SITE_MEDIA_URL, 'static/')
FILEBROWSER_URL_FILEBROWSER_MEDIA = posixpath.join(STATIC_URL, 'filebrowser/')

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

STATICFILES_MEDIA_DIRNAMES = (
    'media',
    'static',
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "homepage.core.finders.AppMediaDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't%o@7x0*zc^r*4@=@*ky=m%_^its#b)t0f9m%fu88(vpt*&8-t'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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

ROOT_URLCONF = 'homepage.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',

    # Third party
    'south',
    'sorl.thumbnail',
    'filebrowser',
    'pagination',
    'tagging',
    'disqus',

    # app
    'homepage.core',
    'homepage.blog',
)

# Need this to get around a bugs in HttpResponseRedirect
# for non-ascii urls and flatpages
APPEND_SLASH=False

# django-tagging
FORCE_LOWERCASE_TAGS=True

# django-pagination
PAGINATION_DEFAULT_PAGINATION = 9
PAGINATION_INVALID_PAGE_RAISES_404 = True 
PAGINATION_DEFAULT_WINDOW = 3

# django-disqus
DISQUS_API_KEY = ''
DISQUS_WEBSITE_SHORTNAME = ''

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'stderr': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class':'logging.StreamHandler',
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
        'django.request': {
            'handlers': ['mail_admins'],
            'propagate': False,
            'level':'WARNING',
        },
    }
}

LOGGING['loggers'][''] = {
    'handlers': ['stdout'],
    'level': 'DEBUG',
}

#HGPROXY_REPO_LIST_REQUIRES_LOGIN = True
#HGPROXY_STATIC_URL = '/hgstatic/' 

INTERNAL_IPS = (
    '127.0.0.1',        
)

SOUTH_MIGRATION_MODULES = {
    "blog": "migrations.blog",
    "tagging": "migrations.tagging",
    "thumbnail": "migrations.thumbnail",
}

#try:
#    import feedparser
#    feedparser._debug = DEBUG
#except ImportError:
#    pass
