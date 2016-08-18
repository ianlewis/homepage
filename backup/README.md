# Homepage Backup

This directory contains the database backup scripts for my homepage. Database
backups are done by periodically running a job in the Kubernetes cluster.

The job runs mysql dump on the database and pipes it to gsutil which saves the
data to Cloud Storage.

## Building

Build the image:

    $ docker build -t homepage-backup .

Tag and push the image:

    $ docker tag homepage-backup asia.gcr.io/ianlewis-org/homepage-backup:v1
    $ gcloud docker push asia.gcr.io/ianlewis-org/homepage-backup:v1

## Create the Secrets

```shell
$ kubectl create secret generic homepage-backup-secret --from-file=gsutil.conf
```

## Create the ConfigMap

```shell
$ kubectl create configmap backup-conf --from-literal=bucket.name=<bucket-name>
```

## Run the job

```shell
$ kubectl create -f job.yaml
```
