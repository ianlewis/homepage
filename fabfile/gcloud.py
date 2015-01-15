#:coding=utf8:

import os
import time
import tempfile

from fabric.api import env, local as localexec, settings
from fabric.utils import error


# Used for connecting to google cloud instances. Located here
# so that the file isn't closed and deleted before fabric exits.
_ssh_config = tempfile.NamedTemporaryFile()


def init_env(name):
    # Defaults to Google Cloud SDK default location.
    env.environ = name

    env.ssh_config_path = _ssh_config.name
    env.ssh_key_path = os.environ.get('COMPUTE_ENGINE_SSH_KEY_FILE',
                                      '~/.ssh/google_compute_engine')

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

    env.create_func = create
    env.halt_func = halt
    env.destroy_func = destroy

    # Get the Google Cloud ssh config
    config_ssh(warn_only=True)


def config_ssh(warn_only=False):
    # Get the vagrant ssh config
    with settings(warn_only=warn_only):
        localexec('gcloud compute config-ssh '
                  '--project %(project_id)s '
                  '--ssh-config-file %(ssh_config_path)s '
                  '--ssh-key-file %(ssh_key_path)s' % env)


def create():
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

    # Need to get the Google Cloud ssh config after
    # booting the instance.
    config_ssh()


def halt():
    # TODO
    error("Not implemented yet.")


def destroy():
    # TODO
    error("Not implemented yet.")
