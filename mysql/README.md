# MySQL

This directory contains manifests for deploying a single MySQL server.

# Create the Volume

Create the volume in Kubernetes. We replace the PD name here because it's
a global identifier and you may want one for multiple namespaces.

```console
$ sed "s/GCE_PD_NAME/mysql-data/" volume.yaml | kubectl create -f -
```

Next create the volume claim:

```console
$ kubectl create -f claim.yaml
```

# Create the Secret

A secret is needed to hold the MySQL root password. Generate a
random password and create a secret from that.

```console
$ < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c25 > root-password
$ kubectl create secret generic mysql-secret --from-file=root-password
```

# Deploy

Create the service and deployment.

```console
$ kubectl create -f service.yaml
$ kubectl create -f deploy.yaml
```
