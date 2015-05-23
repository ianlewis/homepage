#!/bin/sh

# Builds a docker image of the homepage app.

set -e

VERSION=`python setup.py --version`
python setup.py sdist
mkdir -p dist/image
mv dist/homepage-${VERSION}.tar.gz dist/image/homepage.tar.gz
cp deploy/Dockerfile dist/image/
docker build -t homepage dist/image/
# Tag with the appropriate version
docker tag homepage gcr.io/ianlewis-org/homepage:v${VERSION}
