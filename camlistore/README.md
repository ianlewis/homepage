# Camlistore

This directory contains info for my [camlistore](https://camlistore.org/)
server. Most cluster services will use this as a backend to store data.

# Build & Push the Docker image

```shell
$ docker build -t camlistored .
$ docker tag camlistored gcr.io/ianlewis-org/camlistored:108f4b7-1
$ gcloud docker push gcr.io/ianlewis-org/camlistored:108f4b7-1
```

# Create a server-config.json

Alter the identity, googlecloudstorage, and mysql keys and save to
`server-config.json`. We will store blobs locally for fast access, as well as
mirror them to Google Cloud Storage.

```json
{
    "auth": "userpass:alice:secret",
    "https": true,
    "httpsCert": "/certs/tls.crt",
    "httpsKey": "/certs/tls.key",

    "listen": ":3179",
    "identity": "XXXXXXXXX",
    "identitySecretRing": "/conf/identity-secring.gpg",

    "blobPath": "/blobs",
    "packRelated": true,

    "googlecloudstorage": "clientId:clientSecret:refreshToken:bucketName[/optional/dir]",

    "mysql": "camlistore@mysql:password",
    "dbNames": {
        "index": "camlistore_index",
        "blobpacked_index": "camlistore_blobpacked_index",
        "ui_thumbcache": "camlistore_ui_thumbcache",
        "queue-sync-to-index": "camlistore_sync_queue"
    }
}
```

# Set up mysql

Create the database. Use the right password.

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

TODO

```shell
# tip: first list your keys in GPG
gpg -K --keyid-format long --with-colons --with-fingerprint

# then export the one you want (look next to `fpr`)
gpg --export -a A4AA3A5BDBD40EA549CABAF9FBC07D6A97016CB3
```

# Create secrets

This creates the secret containing the server-config.json and
identity-secring.gpg that camlistore will use.

```shell
$ kubectl create secret generic camlistore-server-config \
    --from-file=server-config.json \
    --from-file=identity-secring.gpg
```

Create the HTTPS certs secret.
```shell
$ kubectl create secret generic camlistore-tls-certs \
    --from-file=tls.crt \
    --from-file=tls.key
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
