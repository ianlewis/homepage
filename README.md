Homepage
------------------

This is my homepage/blog.

## Google Cloud Platform Setup

*Copied from [Vagrant provider for GCE README)[https://github.com/mitchellh/vagrant-google]*.

Prior to using this plugin, you will first need to make sure you have a
Google Cloud Platform account, enable Google Compute Engine, and create a
Service Account for API Access.

1. Log in with your Google Account and go to
   [Google Cloud Platform](https://cloud.google.com) and click on the
   `Try it now` button.
1. Create a new project and remember to record the `Project ID` you
   specify.
1. Next, visit the [Developers Console](https://console.developers.google.com)
   make sure to enable the `Google Compute Engine` service for your project
   If prompted, review and agree to the terms of service.
1. While still in the Developers Console, go to `API & AUTH`, `Credentials`
   section and click the `Create new Client ID` button.  In the pop-up dialog,
   select the `Service Account` radio button and the click the `Create Client ID`
   button.
1. When prompted, select the `Download private key` button and make sure
   to save this file in a secure and reliable location.  This key file
   will be used to authorize all Vagrant commands available in this plugin.
1. Still on the same page, find the newly created `Service Account` text
   block on the API Access page.  Record the `Email address` (it should end
   with `@developer.gserviceaccount.com`) associated with the new Service
   Account you just created.  You will need this email address and the
   location of the private key file to properly configure this Vagrant plugin.

## Setup

Install a dummy box for Vagrant. This seems to be necessary even though we
aren't using a local provider.

    $ vagrant box add gce https://github.com/mitchellh/vagrant-google/raw/master/google.box

Set the required environment variables for the project that you got from the
Google Cloud Platform Setup.

    $ export GOOGLE_PROJECT_ID=my-project
    $ export GOOGLE_CLIENT_EMAIL=example@developer.gserviceaccount.com
    $ export GOOGLE_KEY_LOCATION=/path/to/privatekey.p12

You can also set the username and path to the ssh key location if you aren't
using the default set up by the Google Cloud SDK.

    $ export COMPUTE_ENGINE_SSH_USERNAME=ian
    $ export COMPUTE_ENGINE_SSH_KEY_PATH=~/.ssh/id_rsa

You can also set the zone to use. The default is us-central1-a.

    $ export COMPUTE_ENGINE_ZONE=asia-east-1b

## Provision

You can start an instance on Google Cloud using vagrant after setting up the
project.

    $ vagrant up
