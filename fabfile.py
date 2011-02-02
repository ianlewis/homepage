#:coding=utf8:
from fabric.api import *
from fabric.decorators import runs_once

@runs_once
def reboot():
    run("source %(venv_path)s/bin/activate;%(app_path)s/apache2/bin/restart" % env)

@runs_once
def hg_pull():
    run("cd %(app_path)s/hp;hg pull -r %(rev)s" % env)

@runs_once
def hg_update():
    run("cd %(app_path)s/hp;hg update -C -r %(rev)s" % env)

@runs_once
def install_prereqs():
    run("source %(venv_path)s/bin/activate;cd %(app_path)s/hp;pip install -E %(venv_path)s -r requirements.txt" % env)

# Needed until South can support reusable apps transparently
@runs_once
def run_syncdb():
    #run("source %(venv_path)s/bin/activate;cd %(app_path)s/hp;python manage.py syncdb --settings=%(settings)s" % env)
    pass

@runs_once
def collect_static():
    run("source %(venv_path)s/bin/activate;cd %(app_path)s/hp;python manage.py collectstatic --settings=%(settings)s" % env)
    run("mkdir -p %(app_path)s/hp/site_media/media;" % env)

@runs_once
def run_migration():
    run("source %(venv_path)s/bin/activate;cd %(app_path)s/hp;python manage.py migrate --settings=%(settings)s" % env)

@runs_once
def compress_css():
    require("hosts", provided_by=[production])
    run("source %(venv_path)s/bin/activate;rm -f %(app_path)s/hp/site_media/static/css/all.min.css;for FILE in %(app_path)s/hp/site_media/static/css/*.css; do csstidy $FILE --template=highest $FILE.tmp; done;for FILE in %(app_path)s/hp/site_media/static/css/*.tmp; do cat $FILE >> %(app_path)s/hp/site_media/static/css/all.min.css; done;rm -f %(app_path)s/hp/site_media/static/css/*.tmp" % env)

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
    put("settings_production.py", "/home/ianlewis/webapps/homepage/hp/settings_local.py")

def deploy():
    require("hosts", provided_by=[production])
    pull()
    update()
    put_settings()
    migrate_db()
    collect_static()
    compress_css()
    reboot()

def production():
    env.user = 'ianlewis'
    env.hosts = ['ianlewis.webfactional.com']
    env.rev = 'default' 
    env.settings = 'settings_local'
    env.app_path = '~/webapps/homepage'
    env.venv_path = '~/webapps/homepage/venvs/homepage'
