# MySQL

This directory contains manifests for deploying a single MySQL server.

# Create the Volume

Create the volume in Kubernetes. We replace the PD name here because it's
a global identifier and you may want one for multiple namespaces.

```shell
$ sed "s/GCE_PD_NAME/mysql-data/" volume.yaml | kubectl create -f -
```

Next create the volume claim:

```shell
$ kubectl create -f claim.yaml
```

# Deploy

Create the service and deployment.

```shell
$ kubectl create -f service.yaml
$ kubectl create -f deploy.yaml
```
