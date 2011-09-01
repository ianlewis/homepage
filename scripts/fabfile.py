#:coding=utf8:

from __future__ import with_statement 

import os

from fabric.api import *
from fabric.decorators import runs_once

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _run_app_cmd(cmd):
    with prefix('source %(venv_path)s/bin/activate' % env):
        with cd('%(app_path)s/app' % env):
            sudo(cmd)

@runs_once
def reboot():
    # Need to wait for gunicorn to daemonize
    _run_app_cmd('%(app_path)s/scripts/gunicorn.sh reload && sleep 5' % env)

@runs_once
def hg_pull():
    _run_app_cmd('hg pull -r %(rev)s' % env)

@runs_once
def hg_update():
    _run_app_cmd('hg update -C -r %(rev)s' % env)

@runs_once
def install_prereqs():
    _run_app_cmd('pip install -E %(venv_path)s -r %(app_path)s/requirements.txt' % env)

# Needed until South can support reusable apps transparently
@runs_once
def run_syncdb():
    _run_app_cmd("python manage.py syncdb --settings=%(settings)s" % env)

@runs_once
def collect_static():
    _run_app_cmd("python manage.py collectstatic --noinput --settings=%(settings)s" % env)
    sudo("mkdir -p %(app_path)s/site_media/media;" % env)

@runs_once
def run_migration():
    _run_app_cmd("python manage.py migrate --settings=%(settings)s" % env)

@runs_once
def compress_css():
    require("hosts", provided_by=[production])
    _run_app_cmd("rm -f %(app_path)s/site_media/static/css/all.min.css;for FILE in %(app_path)s/site_media/static/css/*.css; do csstidy $FILE --template=highest $FILE.tmp; done;for FILE in %(app_path)s/site_media/static/css/*.tmp; do cat $FILE >> %(app_path)s/site_media/static/css/all.min.css; done;rm -f %(app_path)s/site_media/static/css/*.tmp" % env)

@runs_once
def pull():
    require('hosts', provided_by=[production])
    hg_pull()
    hg_update()

@runs_once
def update():
    require("hosts", provided_by=[production])
    install_prereqs() 

@runs_once
def migrate_db():
    require("hosts", provided_by=[production])
    #run_syncdb() 
    run_migration()

@runs_once
def put_settings():
    require("hosts", provided_by=[production])
    put("%s/app/settings_production.py" % ROOT_PATH, "%(app_path)s/app/settings_local.py" % env, use_sudo=True)

def deploy():
    require("hosts", provided_by=[production])
    pull()
    update()
    put_settings()
    run_syncdb()
    migrate_db()
    collect_static()
    compress_css()
    reboot()

def production():
    env.user = 'ubuntu'
    env.hosts = ['ec2-175-41-217-89.ap-northeast-1.compute.amazonaws.com']
    env.rev = 'default' 
    env.settings = 'settings_local'
    env.app_path = '/var/www/vhosts/homepage'
    env.venv_path = '/var/www/venvs/homepage'
