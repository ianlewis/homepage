#:coding=utf8:

import os
import time
import tempfile

from fabric.api import (
    local as localexec, sudo, env,
    put, run, settings, open_shell,
)
from fabric.tasks import execute
from fabric.decorators import roles, task, runs_once
from fabric.context_managers import prefix

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env.venv_path = '/var/www/venvs/homepage'
env.deploy_user = 'www-data'

if env.ssh_config_path and os.path.isfile(
        os.path.expanduser(env.ssh_config_path)):
    env.use_ssh_config = True

# Used for connecting to vagrant or google cloud. Located here
# so that the file isn't closed and deleted before fabric exits.
_ssh_config = tempfile.NamedTemporaryFile()


def virtualenv(path=None):
    sudo('mkdir -p `dirname %(venv_path)s`' % env)
    sudo('chown %(deploy_user)s:%(deploy_user)s `dirname %(venv_path)s`' % env)

    sudo('if [ ! -d %(venv_path)s ];then '
         '  virtualenv %(venv_path)s;'
         'fi' % env, user=env.deploy_user)
    return prefix('source %(venv_path)s/bin/activate' % env)


@task
def ssh():
    """
    Open an interactive shell to a host. If multiple hosts are defined then
    a host argument must be specified.
    """
    open_shell()


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def restart():
    """
    Restart the application.
    """
    sudo('supervisorctl restart homepage')


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
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
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
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


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def up():
    """
    Bring up the environment.
    """
    env.create_func()


def _gcloud_create():
    # Create instance.
    localexec(
        'gcloud compute --project "%(project_id)s" instances create "%(environ)s" '  # NOQA
        '--zone "%(zone)s" '
        '--machine-type "f1-micro" '
        '--network "default" '
        '--maintenance-policy "MIGRATE" '
        '--scopes "https://www.googleapis.com/auth/devstorage.read_only" '
        '--tags "http-server" "https-server" '
        '--image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1404-trusty-v20141212" '  # NOQA
        '--no-boot-disk-auto-delete '
        '--boot-disk-type "pd-standard" '
        '--boot-disk-device-name "%(environ)s"' % env
    )

    # Sleep to wait for ssh to be available.
    time.sleep(15)


@runs_once
def _local_create():
    localexec("vagrant up --no-provision")

    # Need to get the vagrant ssh config after
    # booting the instance.
    localexec("vagrant ssh-config --host local.virtualbox >> %s"
              % env.ssh_config_path)


@task
@runs_once
def provision():
    """
    Provision the environment using ansible.
    """
    # Write an inventory to use with ansible.
    _inventory = tempfile.NamedTemporaryFile()
    for name, hosts in env.roledefs.items():
        _inventory.write("[%(name)s]\n%(hosts)s\n\n" % {
            'name': name,
            'hosts': "\n".join(hosts),
        })
    _inventory.write("[%(environ)s:children]\n" % env)
    for name in env.roledefs:
        _inventory.write("%s\n" % name)
    _inventory.flush()

    localexec(
        'PYTHONUNBUFFERED=1 '
        'ANSIBLE_HOST_KEY_CHECKING=false '
        'ANSIBLE_SSH_ARGS=\'-F %(ssh_config_path)s -o UserKnownHostsFile=/dev/null -o ControlMaster=auto -o ControlPersist=60s\' '  # NOQA
        'ansible-playbook '
        '--private-key=%(ssh_key_path)s '  # NOQA
        '--user=%(user)s '
        '--connection=ssh '
        '--limit=\'%(environ)s\' '
        '--inventory-file=%(inventory)s '
        'provisioning/site.yml' % {
            'environ': env.environ,
            'user': env.user,
            'ssh_config_path': env.ssh_config_path,
            'ssh_key_path': env.ssh_key_path,
            'inventory': _inventory.name,
        }
    )

# TODO: halt, destroy commands.


@task
def local():
    """
    Local Vagrant environment
    """
    env.environ = 'local'

    # Setup the ssh config so that fabric connects to vagrant.
    env.user = 'vagrant'
    env.ssh_config_path = _ssh_config.name
    env.use_ssh_config = True
    env.ssh_key_path = '~/.vagrant.d/insecure_private_key'

    # Get the vagrant ssh config
    with settings(warn_only=True):
        localexec("vagrant ssh-config --host local.virtualbox >> %s"
                  % env.ssh_config_path)

    env.roledefs.update({
        'webservers': ['local.virtualbox'],  # matches the vagrant ssh-config
        'appservers': ['local.virtualbox'],
        'dbservers': ['local.virtualbox'],
        'cacheservers': ['hoge', 'local.virtualbox'],
    })

    env.create_func = _local_create


@task
def staging():
    """
    Google Compute Engine staging environment
    """
    env.environ = "staging"
    _gcloud()


@task
def production():
    """
    Google Compute Engine production environment
    """
    env.environ = "production"
    _gcloud()


def _gcloud():
    # TODO: gcloud ssh config
    env.ssh_key_path = '~/.ssh/google_compute_engine'

    env.project_id = os.environ.get('GOOGLE_PROJECT_ID')
    env.zone = os.environ.get('COMPUTE_ENGINE_ZONE')

    # So that it matches ssh config file as created by
    # gcloud compute config-ssh
    host = '%s.%s.%s' % (
        env.environ,
        env.zone,
        env.project_id,
    )

    # These roles match the ansible groups
    env.roledefs.update({
        'webservers': [host],
        'appservers': [host],
        'dbservers': [host],
        'cacheservers': [host],
    })

    env.create_func = _gcloud_create
