#!/bin/sh

# Builds a docker image of the homepage app.

set -e

VERSION=`python setup.py --version`
rm -rf homepage/site_media
pip install -r requirements.txt
python setup.py sdist
mv dist/homepage-${VERSION}.tar.gz dist/homepage.tar.gz
