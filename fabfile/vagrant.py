#:coding=utf8:

import tempfile

from fabric.api import local as localexec, env, settings
from fabric.decorators import runs_once


# Used for connecting to vagrant machines. Located here
# so that the file isn't closed and deleted before fabric exits.
_ssh_config = tempfile.NamedTemporaryFile()


def init_env(name):
    env.environ = name

    # Setup the ssh config so that fabric connects to vagrant.
    env.user = 'vagrant'
    env.ssh_config_path = _ssh_config.name
    env.use_ssh_config = True
    env.ssh_key_path = '~/.vagrant.d/insecure_private_key'

    # matches the vagrant ssh-config
    host = 'local.virtualbox'

    env.roledefs.update({
        'webservers': [host],
        'appservers': [host],
        'dbservers': [host],
        'cacheservers': [host],
    })

    env.create_func = create
    env.halt_func = halt
    env.destroy_func = destroy

    config_ssh(warn_only=True)


def config_ssh(warn_only=False):
    # Get the vagrant ssh config
    with settings(warn_only=warn_only):
        localexec("vagrant ssh-config --host local.virtualbox >> %s"
                  % env.ssh_config_path)

    # NOTE: Remove the cached ssh config data.
    if '_ssh_config' in env:
        # NOTE: env is a dict so del env._ssh_config doesn't work
        del env['_ssh_config']


@runs_once
def create():
    """
    Create a vagrant instance.
    """

    # TODO: Currenly runs_once because vagrant up brings up all
    # machines. Only bring up a single machine here?
    localexec("vagrant up --no-provision")

    # Need to get the vagrant ssh config after
    # booting the instance.
    config_ssh()


@runs_once
def halt():
    """
    Halt all vagrant machines.
    """
    # TODO: Currenly runs_once because vagrant halt stops all
    # machines. Only bring up a single machine here?
    localexec("vagrant halt")


@runs_once
def destroy(force=False):
    """
    Destroy all vagrant machines.
    """
    options = ""
    if force:
        options = "--force"
    # TODO: Currenly runs_once because vagrant destroy deletes all
    # machines. Only bring up a single machine here?
    localexec("vagrant destroy " + options)  # NOTE: Interactive
