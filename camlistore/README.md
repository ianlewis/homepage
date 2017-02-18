# Camlistore

This directory contains info for my [camlistore](https://camlistore.org/)
server. Most cluster services will use this as a backend to store data.

# Build & Push the Docker image

```shell
$ docker build -t camlistored .
$ docker tag camlistored gcr.io/ianlewis-org/camlistored:108f4b7-1
$ gcloud docker push gcr.io/ianlewis-org/camlistored:108f4b7-1
```

# Set up mysql

I'm using mysql for [indexing](https://camlistore.org/doc/overview) of
Camlistore objects. You can use other storage backends as well.

This depends on having [MySQL](../mysql/) set up so do that first.

Create the database. Use the right password. I'm using the `camtool` utility
to initialize the necessary databases. You will need to build the utility
by following the [Camlistore getting started guide](https://camlistore.org/download).

```shell
$ kubectl port-forward mysql 3306:3306 &
$ camtool dbinit --user=root --password=rootpassword --host=localhost --dbname=camlistore_index --wipe
$ camtool dbinit --user=root --password=rootpassword --host=localhost --dbname=camlistore_blobpacked_index --wipe
$ camtool dbinit --user=root --password=rootpassword --host=localhost --dbname=camlistore_ui_thumbcache --wipe
$ camtool dbinit --user=root --password=rootpassword --host=localhost --dbname=camlistore_sync_queue --wipe
$ killall kubectl
```

Set up authorization.

```shell
kubectl exec mysql -ti -- \
    bash -c "echo \"GRANT ALL ON camlistore_index.* TO 'camlistore'@'%' IDENTIFIED BY 'password';\" \
    | mysql -u root -p"
```
```shell
kubectl exec mysql -ti -- \
    bash -c "echo \"GRANT ALL ON camlistore_blobpacked_index.* TO 'camlistore'@'%' IDENTIFIED BY 'password';\" \
    | mysql -u root -p"
```
```shell
kubectl exec mysql -ti -- \
    bash -c "echo \"GRANT ALL ON camlistore_ui_thumbcache.* TO 'camlistore'@'%' IDENTIFIED BY 'password';\" \
    | mysql -u root -p"
```
```shell
kubectl exec mysql -ti -- \
    bash -c "echo \"GRANT ALL ON camlistore_sync_queue.* TO 'camlistore'@'%' IDENTIFIED BY 'password';\" \
    | mysql -u root -p"
```

# Create gpg secring

Camlistore uses a key in a secret gpg keyring to sign objects that are created.

I created a keyring using gpg.

```shell
$ gpg --gen-key
...
$ cp ~/.gnupg/secring.gpg .
```

You will also need to add the key identity to the server-conf.json.
It's the string shown as BBBBBBBB below.

```shell
$ gpg --list-key
/home/ian/.gnupg/pubring.gpg
----------------------------
pub   AAAAA/BBBBBBBB 2016-08-18
uid                  Ian Lewis <ianlewis@example.com>
sub   CCCCC/DDDDDDDD 2016-08-18
```

# Create config

This creates the secret containing the server-config.json and
identity-secring.gpg that camlistore will use.

```shell
$ kubectl create configmap camlistore-server-config \
    --from-file=server-config.json
```

Create a secret for the keyring.

```shell
$ kubectl create secret generic camlistore-keyring \
    --from-file=identity-secring.gpg
```

Create a ConfigMap for the nginx proxy.

```shell
$ kubectl create configmap camlistore-nginx-conf \
    --from-file=nginx.conf
```

Create a username & password for access and create a secret for it.

```shell
$ htpasswd -c htpasswd user
New password: 
Re-type new password: 
Adding password for user user

$ kubectl create secret generic camlistore-nginx \
    --from-file=htpasswd
```

# Create the needed volumes.

A persistent disk is needed to store local blobs. We mirror
blobs locally for fast access.

Create the persistent disk on GCE:

```shell
$ gcloud compute disks create camlistore-blobs --size 200GB
```

Create the volume in Kubernetes. We replace the PD name here so you
could use this file in multiple namespaces.

```shell
$ sed "s/GCE_PD_NAME/camlistore-blobs/" volume.yaml | kubectl create -f -
```

Create the volume claim:

```shell
$ kubectl create -f claim.yaml
```

# Deploy the app

Create the service and deployment.

```shell
$ kubectl create -f service.yaml
$ kubectl create -f deploy.yaml
```
