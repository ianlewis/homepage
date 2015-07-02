#!/bin/sh

# Builds a docker image of the homepage app.

set -e

VERSION=`python setup.py --version`
python setup.py sdist
mkdir -p dist/image
mv dist/homepage-${VERSION}.tar.gz dist/image/homepage.tar.gz

# Only copy the requirements.txt if it's different from the
# on in the dist directory.
rsync --checksum requirements.txt dist/image/

cp deploy/Dockerfile dist/image/
docker build -t homepage dist/image/
# Tag with the appropriate version
docker tag homepage gcr.io/ianlewis-org/homepage:${VERSION}

# Export to Container Registry
gcloud docker push gcr.io/ianlewis-org/homepage:${VERSION}
