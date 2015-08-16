#!/bin/sh

# Builds a docuker image for webfront

mkdir -p dist/webfront

set -e

VERSION=1.0.3

# Build a really static binary.
CGO_ENABLED=0 go install -a -ldflags '-s' -installsuffix cgo bitbucket.org/IanLewis/webfront

cp $GOPATH/bin/webfront dist/webfront/webfront
cp deploy/Dockerfile-webfront dist/webfront/Dockerfile
docker build -t webfront dist/webfront/

docker tag webfront gcr.io/ianlewis-org/webfront:${VERSION}

gcloud docker push gcr.io/ianlewis-org/webfront:${VERSION}
