# Homepage

This is my homepage/blog.


## Prerequisites

1. Python 2.7
1. MySQL Client

   You need to have a mysql client installed. Usually that means installing
   the right package.

    ```shell
    $ apt-get install -y libmysqlclient-dev
    ```

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

## Deploy the App

This application is deployed on [Google Container
Engine](https://cloud.google.com/container-engine/), however, any Kubernetes
cluster would do.

### Create the Environment

1. Create secrets for the homepage app. The secrets file should something like
   the file below. Each value should be encoded in base64. See the [secrets
   doc](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/) for more info.
   Save the file to homepage-secrets.yaml.

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
    $ kubectl apply -f homepage-secrets.yaml
    ```

### Build the Docker Images

Building a Docker image should be straight-forward. Give the image a tag that matches the repository url you want and give it a version label.

```shell
$ docker build -t gcr.io/ianlewis-org/homepage:<VERSION> .
```

### Deploy the Application

This app depends on MySQL so you need to deploy that app first.

Deploy the homepage app.

```shell
$ kustomize build kubernetes/staging | kubectl apply -f -
```

## Running Migrations

Migrations are run by running a Job using the Kubernetes
[Jobs API](http://kubernetes.io/docs/user-guide/jobs/).

```shell
$ kubectl apply -f kubernetes/extras/migrate.yaml
```

## Creating Superusers

Creating superusers is done by running a Job using the Kubernetes
[Jobs API](http://kubernetes.io/docs/user-guide/jobs/).

```shell
$ kubectl apply -f kubernetes/extras/createsuperuser-job.yaml
```

This will create a superuser with the username and password "admin". You will
need to login and update the password of this user immediately after creation.
