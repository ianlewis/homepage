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

# Deploying the App Locally

You can provision a VM locally with vagrant and deploy to it.

1. Install vagrant
1. Install ansible:

        $ pip install ansible

1. Deploy and provision the app:

        $ fab env.local vm.up vm.provision app.deploy

1. You should then be able to access the app at http://192.168.33.10/

# Deploy Staging or Production

You can deploy staging, and production environments to Google Cloud Platform.

1. Install [ansible](http://www.ansible.com/):

        $ pip install ansible

1. Install the [Google Cloud Platform SDK](https://cloud.google.com/sdk/).
1. Create a project in the [Google Cloud Platform console](http://console.developers.google.com/).
1. Set the id of your new project:

        $ gcloud config set project <PROJECT>

1. Set the zone you want the app to run in:

        $ gcloud config set compute/zone asia-east1-b

1. Deploy and provision the app:

        $ fab env.staging vm.up vm.provision app.deploy

You can also set the path to the ssh key location if you aren't
using the default set up by the Google Cloud SDK.

    $ export COMPUTE_ENGINE_SSH_KEY_PATH=~/.ssh/id_rsa

# SSH

You can ssh into the created VM easily:

    $ fab env.<environment> vm.ssh
