#:coding=utf8:

import os
import time
import tempfile

import ConfigParser
from StringIO import StringIO

from fabric.api import env, local as localexec, settings, hide, abort
from fabric.colors import green, cyan


# Used for connecting to google cloud instances. Located here
# so that the file isn't closed and deleted before fabric exits.
_ssh_config = tempfile.NamedTemporaryFile()


def init_env(name):
    """
    Initialize the Google Cloud Platform environment.
    """
    env.environ = name

    env.ssh_config_path = _ssh_config.name
    env.use_ssh_config = True

    # Defaults to Google Cloud SDK default location.
    env.ssh_key_path = os.environ.get('COMPUTE_ENGINE_SSH_KEY_FILE',
                                      '~/.ssh/google_compute_engine')
    env.project_id = None
    env.zone = 'us-central1-b'

    parser = ConfigParser.SafeConfigParser()
    try:
        # Read the gcloud SDK config.
        # NOTE: (unset) causes parse errors so replace it with empty values.
        config_file = StringIO(localexec("gcloud config list --all",
                                         capture=True).replace("(unset)", "="))
        parser.readfp(config_file)
        env.project_id = parser.get('core', 'project')
        env.zone = parser.get('compute', 'zone') or env.zone
    except ConfigParser.Error:
        pass

    if not env.project_id:
        abort("Could not detect Google Cloud Platform project.  "
              "Set the default project using \n"
              "'gcloud config set project <PROJECT>'")

    print("")
    print("Project: %s" % cyan(env.project_id))
    print("Zone: %s" % cyan(env.zone))
    print("")

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
    # NOTE: Remove the cached ssh config data.
    if '_ssh_config' in env:
        # NOTE: env is a dict so del env._ssh_config doesn't work
        del env['_ssh_config']


def create():
    # Check if the instance already exists
    exists = False
    with hide('stdout', 'stderr'):
        with settings(warn_only=True):
            result = localexec(
                'gcloud compute --project "%(project_id)s" instances describe "%(environ)s" '  # NOQA
                '--zone "%(zone)s" ' % env
            )
            exists = result.return_code == 0

    # Skip creation if the instance is already created.
    if exists:
        print(green("Instance already created."))
    else:
        # Create instance.
        print(green("Creating instance."))
        localexec(
            'gcloud compute --project "%(project_id)s" instances create "%(environ)s" '  # NOQA
            '--zone "%(zone)s" '
            '--machine-type "f1-micro" '
            '--network "default" '
            '--maintenance-policy "MIGRATE" '
            '--scopes "https://www.googleapis.com/auth/devstorage.read_only" '
            '--tags "http-server" "https-server" '
            '--image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1404-trusty-v20141212" '  # NOQA
            '--boot-disk-type "pd-standard" '
            '--boot-disk-device-name "%(environ)s"' % env
        )

        # Sleep to wait for ssh to be available.
        time.sleep(15)

    # Need to get the Google Cloud ssh config after
    # booting the instance.
    config_ssh()


def halt():
    """
    Stop the Google Cloud Instance
    """
    print(green("Stopping instance."))

    localexec(
        'gcloud compute --project "%(project_id)s" instances stop "%(environ)s" '  # NOQA
        '--zone "%(zone)s"' % env
    )


def destroy(force=False):
    """
    Delete the Google Cloud Instance.
    """
    print(green("Deleting instance."))

    options = ""
    if force:
        options = "--quiet"
    # NOTE: Interactive
    localexec(
        ('gcloud compute --project "%(project_id)s" instances delete "%(environ)s" '  # NOQA
         '--zone "%(zone)s" ' + options) % env
    )
