Homepage
------------------

This is my homepage/blog.

# Development

Create a virtualenv

    $ mkvirtualenv homepage

Install the development requirements

    $ python setup.py develop

Run the development server in debug mode

    $ python manage.py runserver

# Local Setup

TODO: Clean this up

1. Install vagrant
1. Install ansible

# Google Cloud Platform Setup

TODO: Clean this up

1. Create a project
1. Install the Google Cloud Platform SDK
1. TODO

## Setup

Set the required environment variables for the project that you got from the
Google Cloud Platform Setup.

    $ export GOOGLE_PROJECT_ID=my-project
    $ export COMPUTE_ENGINE_ZONE=asia-east-1b

You can also set the username and path to the ssh key location if you aren't
using the default set up by the Google Cloud SDK.

    $ export COMPUTE_ENGINE_SSH_USERNAME=ian
    $ export COMPUTE_ENGINE_SSH_KEY_PATH=~/.ssh/id_rsa

# Provisioning

You can start an instance in your local Vagrant or Google Cloud after setting
up the project.

    $ fab <environment> up provision deploy

## Environments

There are three environments that you can provision; local,
staging, and production.

The local environment is run locally using vagrant.

    $ fab local up provision

The staging and production environments use Google Compute Engine. You can
create and provision and instance just as easily as you can locally.

    $ fab staging up provision
