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

## Run the job

    $ kubectl create -f backup.yaml
