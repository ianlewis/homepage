#:coding=utf8:

from fabric.api import (
    env, task, roles,
    prefix, local as localexec, sudo, run, execute,
    put, runs_once,
)

env.venv_path = '/var/www/venvs/homepage'
env.deploy_user = 'www-data'


def virtualenv(path=None):
    sudo('mkdir -p `dirname %(venv_path)s`' % env)
    sudo('chown %(deploy_user)s:%(deploy_user)s `dirname %(venv_path)s`' % env)

    sudo('if [ ! -d %(venv_path)s ];then '
         '  virtualenv %(venv_path)s;'
         'fi' % env, user=env.deploy_user)
    return prefix('source %(venv_path)s/bin/activate' % env)


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def restart():
    """
    Restart the application.
    """
    sudo('supervisorctl restart homepage')


@task
@roles('appservers')
def update():
    """
    Update the application.
    """
    name = localexec("python setup.py --name", capture=True)
    version = localexec("python setup.py --version", capture=True)
    localexec("python setup.py sdist")

    tmp_path = run("mktemp --suffix=.tar.gz")
    put("dist/%s-%s.tar.gz" % (name, version), tmp_path, mode=0755)

    with virtualenv():
        sudo('pip install %s' % tmp_path, user=env.deploy_user)


@task
@runs_once
@roles('appservers')
def migrate_db():
    """
    Migrate the database.
    """
    with virtualenv():
        sudo("homepage migrate", user=env.deploy_user)


@task
@roles('appservers')
def deploy():
    """
    Deploy the latest version of the app
    """
    execute(update)
    execute(migrate_db)
    execute(restart)
