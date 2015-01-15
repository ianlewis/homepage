#:coding=utf8:

import pipes

from fabric.api import (
    env, task, roles,
    prefix, local as localexec, sudo, run, execute,
    put, runs_once, settings,
)

env.venv_path = '/var/www/venvs/homepage'
env.deploy_user = 'supervisord'


def run_su(cmd, user=None):

    # The Google Compute Engine images prompt for a password when running
    # sudo -u so we sudo to root and then su to the user we want to run the
    # command as.
    if user is None:
        user = env.sudo_user or 'root'
    if user == env.user:
        run(cmd)
    else:
        # Temporarily disable prefixes and handle them ourselves.
        # We need to do that so that the prefix takes effect in the
        # shell where the command is executed rather than the shell
        # where su is executed.
        prefixes = list(env.command_prefixes)
        with settings(command_prefixes=[]):

            # Support the prefix() context processor.
            glue = " && "
            prefix = (glue.join(prefixes) + glue) if prefixes else ""
            cmd = prefix + cmd

            # NOTE: Quote the command since it's being run in a shell.
            cmd = "%s %s" % (env.shell, pipes.quote(prefix + cmd))

            # NOTE: Quote again since it's being run under su
            run('sudo su %s -c %s' % (user, pipes.quote(cmd)))


def virtualenv(path=None):
    run_su('mkdir -p `dirname %(venv_path)s`' % env, user=env.deploy_user)
    run_su('if [ ! -d %(venv_path)s ];then '
           '  virtualenv %(venv_path)s;'
           'fi' % env, user=env.deploy_user)
    return prefix('source %(venv_path)s/bin/activate' % env)


@task
@roles('appservers')
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
        run_su('pip install %s' % tmp_path, user=env.deploy_user)


@task
@runs_once
@roles('appservers')
def migrate_db():
    """
    Migrate the database.
    """
    with virtualenv():
        # NOTE: The app runs as supervisord so
        #       we run the migrate command as that user also.
        run_su("homepage migrate", user=env.deploy_user)


@task
@roles('appservers')
def deploy():
    """
    Deploy the latest version of the app
    """
    execute(update)
    execute(migrate_db)
    execute(restart)
