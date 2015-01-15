#:coding=utf-8:

from fabric.api import env, roles, task, open_shell

import ansible


@task
def ssh(host=None):
    """
    Open an interactive shell to a host.
    """
    if env.hosts:
        hosts = env.hosts
    else:
        hosts = list(set(h for r in env.roledefs.values() for h in r))
    if len(hosts) == 1:
        # If there is only one host then use that host. Otherwise prompt
        # for a host.
        env.host_string = hosts[0]
    else:
        print("Valid hosts are:")
        print("")
        for host in hosts:
            print(host)
        print("")
    open_shell()


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def up():
    """
    Bring up the environment.
    """
    env.create_func()


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def halt():
    """
    Terminate VMs.
    """
    env.halt_func()


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def destroy():
    """
    Destroy the VMs.
    """
    env.destroy_func()


@task
@roles('webservers', 'appservers', 'dbservers', 'cacheservers')
def provision():
    """
    Provision the environment using ansible.
    """
    ansible.provision()
