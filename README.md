# Homepage

This is my homepage/blog.

## Development

1. Create a virtualenv

        ```shell
        $ mkvirtualenv homepage
        ```

1. Install the development requirements

        ```shell
        $ python setup.py develop
        ```

1. Run initial migrations

        ```shell
        $ DEBUG=true homepage migrate
        ```

1. Create an "admin" superuser with password "admin"

        ```shell
        $ DEBUG=true homepage createsuperuser
        ```

1. Run the development server in debug mode.

        ```shell
        $ DEBUG=true python manage.py runserver
        ```

   You can also run the production webserver in debug mode but it won't reload
   when code is updated.

        ```shell
        $ DEBUG=true homepage start
        ```

## Deploy Staging or Production

You can deploy staging, and production environments to Google Cloud Platform.
There are a number of scripts for deploying to [Google Container
Engine](https://cloud.google.com/container-engine/).

### Create and Setup a Cloud Platform Project

1. Install the [Google Cloud Platform SDK](https://cloud.google.com/sdk/).
1. Create a project in the [Google Cloud Platform console](http://console.developers.google.com/).
1. Authenticate the Google Cloud Platform SDK:

        ```shell
        $ gcloud auth login
        ```

1. Set the id of your new project:

        ```shell
        $ gcloud config set project <PROJECT>
        ```

1. Set the zone you want the app to run in:

        ```shell
        $ gcloud config set compute/zone asia-east1-b
        ```

1. Create a Container Engine Cluster. You may need to specify other options,
   such as the size of the cluster, VM type etc.

        ```shell
        $ gcloud container clusters create homepage-cluster
        ```

### Create the Environment

1. Create namespaces for staging and production.

        ```shell
        $ kubectl create -f deploy/homepage-staging-ns.yaml
        $ kubectl create -f deploy/homepage-staging-prod.yaml
        ```

1. Create secrets for each environment. The secrets file should something like
   the file below. Each value should be encoded in base64. See the [secrets
   doc](http://kubernetes.io/v1.0/docs/user-guide/secrets.html) for more info.

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: homepage-secret
    data:
      secret-key: ...
      disqus-api-key: ...
      disqus-website-shortname: ...
      db-user: ...
      db-password: ...
    ```

1. Deploy the secrets to the cluster.

        ```shell
        $ kubectl create -f staging-secrets.yaml --namespace=homepage-staging
        $ kubectl create -f webfront-secrets-staging.yaml --namespace=homepage-staging
        $ kubectl create -f prod-secrets.yaml --namespace=homepage-prod
        $ kubectl create -f webfront-secrets-prod.yaml --namespace=homepage-prod
        ```

### Build the Docker Images

There is a handy build script in the `bin` directory you can run to build
and push the app image.

    ```shell
    $ ./bin/build.sh
    ```

This script will build a Python package for the app, build a Docker image, and
push it to [Google Container Registry](https://cloud.google.com/container-registry/).

### Deploy the Application

1. Deploy the database.

        ```shell
        $ kubectl create -f deploy/mysql/mysql.yaml --namespace=<namespace> 
        $ kubectl create -f deploy/mysql/mysql-service.yaml --namespace=<namespace> 
        ```

1. Deploy the homepage app.

        ```shell
        $ kubectl create -f deploy/homepage-rc.yaml --namespace=<namespace>
        $ kubectl create -f deploy/homepage-service.yaml --namespace=<namespace>
        ```

### Creating the MySQL database

You can create the MySQL database by running the "CREATE DATABASE" query inside the mysql database container after it's running.

    ```shell
    $ kubectl exec mysql --namespace=<namespace> -- bash -c "echo 'CREATE DATABASE IF NOT EXISTS homepage CHARACTER SET utf8;' | mysql -u root --password=yourpassword"
    ```

## Running Migrations

Migrations are run in staging or production by running a pod in Container
Engine.

    ```shell
    $ kubectl create -f deploy/homepage-migrate-pod.yaml --namespace=<namespace>
    ```

The pod will be created with the name "homepage-migrate". Since it exits
normally, in order to preserve info and logs, Container Engine keeps the pod
around. In order to run the migration again, you need clean up by deleting the
previous pod.

    ```shell
    $ kubectl delete pod homepage-migrate --namespace=<namespace>
    ```

## Creating Superusers

Creating superusers is done by running a pod in Container Engine.

    ```shell
    $ kubectl create -f deploy/homepage-createsuperuser-pod.yaml --namespace=<namespace>
    ```

This will create a superuser with the username and password "admin". You will
need to login and update the password of this user immediately after creation.
