#:coding=utf8:
#from fabric.api import run,config

DEPLOY_USER = 'ianlewis'
DEPLOY_HOSTS = ['ianlewis.webfactional.com']
DEPLOY_REV = 'default'
APP_PATH='~/webapps/homepage'

def reboot():
    run("workon homepage;$(app_path)/apache2/bin/restart")

def hg_pull():
    run("cd $(app_path)/hp;hg pull -r $(rev)")

def hg_update():
    run("cd $(app_path)/hp;hg update -C -r $(rev)")

def install_prereqs():
    run("workon homepage;cd $(app_path)/hp;pip install -r requirements.txt")

# Needed until South can support reusable apps transparently
def run_syncdb():
    run("workon homepage;cd $(app_path)/hp;python manage.py syncdb")

def run_migration():
    run("workon homepage;cd $(app_path)/hp;python manage.py migrate")

def compress_css():
    require("fab_hosts", provided_by=[production])
    run("workon homepage;rm -f $(app_path)/hp/static/css/all.min.css;for FILE in $(app_path)/hp/static/css/*.css; do csstidy $FILE --template=highest $FILE.tmp; done;for FILE in $(app_path)/hp/static/css/*.tmp; do cat $FILE >> $(app_path)/hp/static/css/all.min.css; done;rm -f $(app_path)/hp/static/css/*.tmp" )

def pull():
    require('fab_hosts', provided_by=[production])
    invoke(hg_pull)
    invoke(hg_update)

def update():
    require("fab_hosts", provided_by=[production])
    invoke(install_prereqs) 

def migrate_db():
    require("fab_hosts", provided_by=[production])
    invoke(run_syncdb) 
    invoke(run_migration)

def put_settings():
    require("fab_hosts", provided_by=[production])
    put("settings_production.py", "/home/ianlewis/webapps/homepage/hp/settings_local.py")

def deploy():
    require("fab_hosts", provided_by=[production])
    invoke(pull)
    invoke(update)
    invoke(migrate_db)
    invoke(compress_css)
    invoke(put_settings)
    invoke(reboot)

def production():
    config.fab_user = DEPLOY_USER
    config.fab_hosts = DEPLOY_HOSTS
    config.rev = DEPLOY_REV
    config.app_path = APP_PATH 
