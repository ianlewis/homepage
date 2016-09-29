# Cron Controller

This directory contains a simple cron controller. This app implements scheduled jobs.

You can create scheduled jobs using a ThirdPartyResource

## Create the ThirdPartyResource

Create the CronTab ThirdPartyResource object to enable the CronTab API.

```console
$ kubectl create -f resource.yaml
```

CronTab objects can then be created with the following format.

```yaml
apiVersion: "alpha.ianlewis.org/v1"
kind: "CronTab"
metadata:
  name: <name>
spec:
  schedule: "<cron spec>"
  jobTemplate:
    <job template>
```

See an example in the [test-crontab.yaml](test-crontab.yaml) file.

## Building

Build and tag the image:

```console
$ make image
```

Push the image:

```console
$ make push
```

## Deploy

Create the cron-controller deployment.

```console
$ kubectl create -f deploy.yaml
```
