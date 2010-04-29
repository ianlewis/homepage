import os
import sys
import site

PYTHON_PATH = '/home/ianlewis/webapps/homepage/lib/python2.5'
VHOST_PATH = '/home/ianlewis/webapps/homepage'
VENV_PATH = '/home/ianlewis/webapps/homepage/venvs/homepage'
SETTINGS_MOD = 'settings_production'

site.addsitedir(os.path.join(VENV_PATH, 'lib', 'python2.5', 'site-packages'))
# Don't load from this path since it has an old version of django there
#site.addsitedir(os.path.join(PYTHON_PATH, 'lib', 'python2.5', 'site-packages'))

sys.path.insert(0, VHOST_PATH)
sys.path.insert(0, os.path.join(VHOST_PATH, 'hp'))

from django.core.handlers.wsgi import WSGIHandler

os.environ['DJANGO_SETTINGS_MODULE'] = 'hp.settings_local'
application = WSGIHandler()
