# GoCron

This directory contains the gocron app. This app implements scheduled jobs.

## Building

Build the image:

    $ docker build -t gocron .

Tag and push the image:

    $ docker tag gocron asia.gcr.io/ianlewis-org/gocron:v1
    $ gcloud docker push asia.gcr.io/ianlewis-org/gocron:v1

## Create ConfigMaps

    kubectl create configmap crontab --from-file=prod/crontab
    kubectl create configmap backup-job --from-file=../backup/job.yaml
    kubectl create configmap renew-certs-job --from-file=../../renew-certs/job.yaml

## Deploy

    $ kubectl create -f deploy.yaml
