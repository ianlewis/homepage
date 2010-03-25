#:coding=utf8:
from fabric.api import *
from fabric.decorators import runs_once

DEPLOY_USER = 'ianlewis'
DEPLOY_HOSTS = ['ianlewis.webfactional.com']
DEPLOY_REV = 'default'
APP_PATH='~/webapps/homepage'

@runs_once
def reboot():
    run("workon homepage;%(app_path)s/apache2/bin/restart" % env)

@runs_once
def hg_pull():
    run("cd %(app_path)s/hp;hg pull -r %(rev)s" % env)

@runs_once
def hg_update():
    run("cd %(app_path)s/hp;hg update -C -r %(rev)s" % env)

@runs_once
def install_prereqs():
    run("workon homepage;cd %(app_path)s/hp;pip install -r requirements.txt" % env)

# Needed until South can support reusable apps transparently
@runs_once
def run_syncdb():
    run("workon homepage;cd %(app_path)s/hp;python manage.py syncdb" % env)

@runs_once
def run_migration():
    run("workon homepage;cd %(app_path)s/hp;python manage.py migrate" % env)

@runs_once
def compress_css():
    require("hosts", provided_by=[production])
    run("workon homepage;rm -f %(app_path)s/hp/static/css/all.min.css;for FILE in %(app_path)s/hp/static/css/*.css; do csstidy $FILE --template=highest $FILE.tmp; done;for FILE in %(app_path)s/hp/static/css/*.tmp; do cat $FILE >> %(app_path)s/hp/static/css/all.min.css; done;rm -f %(app_path)s/hp/static/css/*.tmp" % env)

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
    run_syncdb() 
    run_migration()

@runs_once
def put_settings():
    require("hosts", provided_by=[production])
    put("settings_production.py", "/home/ianlewis/webapps/homepage/hp/settings_local.py")

def deploy():
    require("hosts", provided_by=[production])
    pull()
    update()
    put_settings()
    migrate_db()
    compress_css()
    reboot()

def production():
    env.user = DEPLOY_USER 
    env.hosts = DEPLOY_HOSTS
    env.rev = DEPLOY_REV
    env.app_path = APP_PATH 
