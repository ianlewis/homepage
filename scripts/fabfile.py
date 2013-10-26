#:coding=utf8:

import os

from fabric.api import cd, sudo, env, put
from fabric.tasks import execute
from fabric.decorators import roles
from fabric.context_managers import prefix

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if env.ssh_config_path and os.path.isfile(os.path.expanduser(env.ssh_config_path)):
    env.use_ssh_config = True

def _run_app_cmd(cmd):
    with prefix('source %(venv_path)s/bin/activate' % env):
        with cd('%(app_path)s/' % env):
            sudo(cmd, user=env.deploy_user)

@roles('webservers')
def delete_pyc():
    u"""
    pyc ファイルをすべて削除する
    """

    # migrations の pyc なども削除するため、 base_path で実行する
    with cd("%(app_path)s" % env):
        # -P 5 で平行で rm 実行する
        # スペースがファイル名に入ると困るので、 -print0 でヌル文字で検索結果を区切る
        # xargs の -0 オプションで、ヌルマジ区切りデータを読み込む

        # daemontools ディレクトリに入らないように -name daemontools -prune を追加
        sudo("""find . -name daemontools -prune -o -name "*.pyc" -print0 | xargs -r -P 5 -n 1 -0 rm""", user=env.deploy_user)

@roles('webservers')
def reboot():
    # Need to wait for gunicorn to daemonize
    execute(delete_pyc)
    sudo('svc -t %(service_path)s' % env)

@roles('webservers')
def hg_pull():
    with cd(env.app_path):
        sudo('hg pull -r %(rev)s' % env, user=env.deploy_user)

@roles('webservers')
def hg_update():
    with cd(env.app_path):
        sudo('hg update -C -r %(rev)s' % env, user=env.deploy_user)

@roles('webservers')
def install_prereqs():
    sudo('pip install -E %(venv_path)s -r %(app_path)s/requirements.txt' % env, user=env.deploy_user)

# Needed until South can support reusable apps transparently
@roles('webservers')
def run_syncdb():
    _run_app_cmd("python manage.py syncdb --settings=%(settings)s" % env)

@roles('webservers')
def collect_static():
    _run_app_cmd("python manage.py collectstatic --noinput --settings=%(settings)s" % env)
    sudo("mkdir -p %(app_path)s/site_media/media;" % env)

@roles('webservers')
def run_migration():
    _run_app_cmd("python manage.py migrate --settings=%(settings)s" % env)

@roles('webservers')
def compress_css():
    sudo("rm -f %(app_path)s/site_media/static/css/all.min.css;for FILE in %(app_path)s/site_media/static/css/*.css; do csstidy $FILE --template=highest $FILE.tmp; done;for FILE in %(app_path)s/site_media/static/css/*.tmp; do cat $FILE >> %(app_path)s/site_media/static/css/all.min.css; done;rm -f %(app_path)s/site_media/static/css/*.tmp" % env, user=env.deploy_user)

@roles('webservers')
def pull():
    hg_pull()
    hg_update()

@roles('webservers')
def update():
    install_prereqs() 

@roles('webservers')
def migrate_db():
    #run_syncdb() 
    run_migration()

@roles('webservers')
def put_settings():
    put("%s/homepage/settings_production.py" % ROOT_PATH, "%(app_path)s/homepage/settings_local.py" % env, use_sudo=True)
    sudo('chown %(deploy_user)s:%(deploy_user)s "%(app_path)s/homepage/settings_local.py"' % env)

@roles('webservers')
def deploy():
    pull()
    update()
    put_settings()
    run_syncdb()
    migrate_db()
    collect_static()
    #compress_css()
    reboot()

def production():
    env.deploy_user = 'www-data'
    env.roledefs.update({
        'webservers': ['www.ianlewis.org'],
    })
    env.rev = 'default' 
    env.settings = 'homepage.settings_local'
    env.app_path = '/var/www/vhosts/homepage'
    env.venv_path = '/var/www/venvs/homepage'
    env.service_path = '/etc/service/homepage'
