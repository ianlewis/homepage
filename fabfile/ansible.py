#:coding=utf8:

import tempfile

from fabric.api import local as localexec, env
from fabric.decorators import runs_once


@runs_once
def provision():
    """
    Run ansible-playbook.
    """

    # TODO: This creates an inventory file and runs
    # for all hosts. Maybe limit to only the current host?

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
        '--ask-vault-pass '
        'provisioning/site.yml' % {
            'environ': env.environ,
            'user': env.user,
            'ssh_config_path': env.ssh_config_path,
            'ssh_key_path': env.ssh_key_path,
            'inventory': _inventory.name,
        }
    )
