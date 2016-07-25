# GoCron

This directory contains the gocron app. This app implements scheduled jobs.

## Get kubectl 

Download the kubectl binary:

    $ curl -O https://storage.googleapis.com/kubernetes-release/release/v1.3.0/bin/linux/amd64/kubectl

## Building

Build the image:

    $ docker build -t gocron .

Tag and push the image:

    $ docker tag gocron asia.gcr.io/ianlewis-org/gocron:v1
    $ gcloud docker push asia.gcr.io/ianlewis-org/gocron:v1

## Create ConfigMaps

    kubectl create configmap crontab --from-file=prod/crontab
    kubectl create configmap backup-job --from-file=../backup/job.yaml

## Deploy

    $ kubectl create -f deploy.yaml
