import os
import sys
import site

VHOST_PATH = '/var/www/vhost/homepage'
VENV_PATH = '/var/www/venvs/homepage'
PYTHON_PATH = os.path.join(VENV_PATH, 'lib', 'python2.5')

site.addsitedir(os.path.join(PYTHON_PATH, 'site-packages'))
# Don't load from this path since it has an old version of django there
#site.addsitedir(os.path.join(PYTHON_PATH, 'lib', 'python2.5', 'site-packages'))

sys.path.insert(0, os.path.join(VHOST_PATH, 'app'))

from django.core.handlers.wsgi import WSGIHandler

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_local'
application = WSGIHandler()
