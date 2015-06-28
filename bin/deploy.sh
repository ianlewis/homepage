#!/bin/sh

# Deploys the app to the given environment (e.g. staging prod).
# The app must have been be previously built

set -e

NAMESPACE="homepage-$1"

kubectl create -f deploy/mysql/mysql.yaml --namespace=${NAMESPACE}
kubectl create -f deploy/mysql/mysql-service.yaml --namespace=${NAMESPACE}

# TODO: Memcached
# kubectl create -f deploy/memcached/memcached.yaml
# kubectl create -f deploy/memcached/memcached-service.yaml

kubectl create -f deploy/homepage-secret.yaml --namespace=${NAMESPACE}
kubectl create -f deploy/homepage-rc.yaml --namespace=${NAMESPACE}
kubectl create -f deploy/homepage-service.yaml --namespace=${NAMESPACE}

# Create the MySQL Database
# kubectl exec mysql --namespace=${NAMESPACE} -- bash -c "echo 'CREATE DATABASE IF NOT EXISTS homepage CHARACTER SET utf8;' | mysql -u root --password=yourpassword"
# kubectl create -f deploy/homepage-migrate-pod.yaml --namespace=${NAMESPACE}
