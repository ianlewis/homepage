#:coding=utf8:

import os

from fabric.api import cd, sudo, env, put
from fabric.decorators import roles
from fabric.context_managers import prefix

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _annotate_hosts_with_ssh_config_info():
    """
    ~/.ssh/config ファイルがあれば、設定を読み込む
    """
    from os.path import expanduser
    from paramiko.config import SSHConfig

    def hostinfo(host, config):
        hive = config.lookup(host)
        if 'hostname' in hive:
            host = hive['hostname']
        if 'user' in hive:
            host = '%s@%s' % (hive['user'], host)
        if 'port' in hive:
            host = '%s:%s' % (host, hive['port'])
        return host

    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError:
        pass
    else:
        config = SSHConfig()
        config.parse(config_file)
        keys = [config.lookup(host).get('identityfile', None)
            for host in env.hosts]
        env.key_filename = [expanduser(key) for key in keys if key is not None]
        env.hosts = [hostinfo(host, config) for host in env.hosts]

        if env.roledefs:
            for roledef, hosts in env.roledefs.items():
                env.roledefs[roledef] = [hostinfo(host, config) for host in hosts]
                keys = [config.lookup(host).get('identityfile', None) for host in hosts]
                env.key_filename.extend([expanduser(key) for key in keys if key is not None])

def _run_app_cmd(cmd):
    with prefix('source %(venv_path)s/bin/activate' % env):
        with cd('%(app_path)s/app' % env):
            sudo(cmd, user=env.deploy_user)

@roles('webservers')
def reboot():
    # Need to wait for gunicorn to daemonize
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
    put("%s/app/settings_production.py" % ROOT_PATH, "%(app_path)s/app/settings_local.py" % env, use_sudo=True)
    sudo('chown %(deploy_user)s:%(deploy_user)s "%(app_path)s/app/settings_local.py"' % env)

@roles('webservers')
def deploy():
    pull()
    update()
    put_settings()
    run_syncdb()
    migrate_db()
    collect_static()
    compress_css()
    reboot()

def production():
    env.deploy_user = 'www-data'
    env.roledefs.update({
        'webservers': ['www.ianlewis.org'],
    })
    env.rev = 'default' 
    env.settings = 'settings_local'
    env.app_path = '/var/www/vhosts/homepage'
    env.venv_path = '/var/www/venvs/homepage'
    env.service_path = '/etc/service/homepage'

    _annotate_hosts_with_ssh_config_info()
