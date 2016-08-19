# Homepage

This repo holds a number of apps that run in my personal
[Kubernetes](http://kubernetes.io/) cluster.

# Apps

- [Homepage](homepage/) - My homepage/blog (www.ianlewis.org)
- [API Server](api/) - API that serves personal data (api.ianlewis.org)
- [Camlistore](camlistore/) - Camlistore to manage personal data
- [MySQL](mysql/) - MySQL database.
- [Backup](backup/) - MySQL database backups.
- [Cron](cron/) - A simple cron server that can run Kubernetes Jobs
- [nginx](nginx/) - Nginx frontend for the homepage/blog
- [renew-certs](renew-certs/) - An attempt at automatic certificate renewal

# Creating a Cluster

My cluster is deployed on [Google Container
Engine](https://cloud.google.com/container-engine/), however, any Kubernetes
cluster would do.

## Create and Setup a Cloud Platform Project

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
