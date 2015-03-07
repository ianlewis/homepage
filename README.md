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

For local setup you will need to have vagrant installed.

# Google Cloud Platform Setup

For Google Cloud Platform you will need to create a project, and 
install the [Google Cloud Platform SDK](https://cloud.google.com/sdk/).

## Setup

Set the required config for the project. You can get the project ID from the
Google Cloud Platform console.

    $ gcloud config set project <PROJECT>

You can set the zone you run the app in.

    $ gcloud config set compute/zone asia-east1-b

You can also set the path to the ssh key location if you aren't
using the default set up by the Google Cloud SDK.

    $ export COMPUTE_ENGINE_SSH_KEY_PATH=~/.ssh/id_rsa

# Provisioning

You can start an instance in your local Vagrant or Google Cloud after setting
up the project.

You will need to have ansible installed. Install it using pip:

    $ pip install ansible

You can then provision and deploy the app:

    $ fab env.<environment> vm.up vm.provision app.deploy

## Environments

There are three environments that you can provision; local,
staging, and production.

The 'local' environment is run locally using vagrant.

    $ fab env.local vm.up vm.provision

The 'staging' and 'production' environments use Google Compute Engine. You can
create and provision and instance just as easily as you can locally.

    $ fab env.staging vm.up vm.provision

You can ssh into the created VM easily:

    $ fab env.<environment> vm.ssh
