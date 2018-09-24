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

I recommend you have a namespace for staging and one for production
but YMMV.

1. Create secrets for the homepage app. The secrets file should something like
   the file below. Each value should be encoded in base64. See the [secrets
   doc](http://kubernetes.io/docs/user-guide/secrets/walkthrough/) for more info.
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

1. Create secrets for the web frontend nginx.

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: webfront-secret
    data:
      webfront-crt: ...
      webfront-key: ...
    ```

1. Deploy the secrets to the cluster.

    ```shell
    $ kubectl create -f homepage-secrets.yaml
    $ kubectl create -f webfront-secrets.yaml
    ```

### Build the Docker Images

There is a handy build script in the `bin` directory you can run to build
and push the app image.

```shell
$ ./build.sh
```

This script will build a Python package for the app, build a Docker image, and
push it to [Google Container Registry](https://cloud.google.com/container-registry/).

### Deploy the Application

This app depends on [MySQL](../mysql/) so you need to deploy that app first.

Deploy the homepage app.

```shell
$ kubectl create -f deploy.yaml
$ kubectl create -f service.yaml
```

### Creating the MySQL database

You can create the MySQL database by running the "CREATE DATABASE" query inside
the mysql database container after it's running.

```shell
$ MYSQL_POD=$(kubectl get pods -o jsonpath='{.items[0].metadata.name}' --selector=name=mysql)
$ kubectl exec $MYSQL_POD -it -- \
    bash -c "echo 'CREATE DATABASE IF NOT EXISTS homepage CHARACTER SET utf8;' \
    | mysql -u root -p"
```

## Running Migrations

Migrations are run by running a Job using the Kubernetes
[Jobs API](http://kubernetes.io/docs/user-guide/jobs/).

```shell
$ kubectl create -f migrate-job.yaml
```

## Creating Superusers

Creating superusers is done by running a Job using the Kubernetes
[Jobs API](http://kubernetes.io/docs/user-guide/jobs/).

```shell
$ kubectl create -f createsuperuser-pod.yaml
```

This will create a superuser with the username and password "admin". You will
need to login and update the password of this user immediately after creation.
