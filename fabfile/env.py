#:coding=utf8:

from fabric.api import task

import vagrant
import gcloud


@task
def local():
    """
    Local Vagrant environment
    """
    vagrant.init_env(name="local")


@task
def staging():
    """
    Google Compute Engine staging environment
    """
    gcloud.init_env(name="staging")


@task
def production():
    """
    Google Compute Engine production environment
    """
    gcloud.init_env(name="production")
