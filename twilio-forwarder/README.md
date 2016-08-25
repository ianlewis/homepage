# Twilio Forwarder

A Twilio phone call forwarding app. This app is similar to Google Voice or
other forwarding services. It is written in Go and is meant to be run in Google
Container Engine.

The app itself uses [Firebase](https://firebase.google.com/) to store info
about how to forward calls and call history. You can edit and view the data
in the [FIrebase Console](https://console.firebase.google.com/)

## Build

You can build the app using make.

```shell
$ make
```

The Docker image can be built using the image command to make.

```shell
$ make image
```

## Deploy

Store the URI to your Firebase database in a file called firebase-uri and the
secret used to authenticate with the database in firebase-secret. Then create the
secret containing info on how to connect to Firebase.

```shell
$ kubectl create secret generic twilio-forwarder-secret --from-file=firebase-uri --from-file=firebase-secret
```

Create the Kubernetes service and deployment to deploy the application.

```shell
$ kubectl create -f service.yaml
$ kubectl create -f deploy.yaml
```
