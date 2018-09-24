#!/bin/bash

HOMEPAGE_VERSION=$SHORT_SHA
if [ "$HOMEPAGE_VERSION" = "" ]; then
    HOMEPAGE_VERSION=$(git rev-parse --short master)
fi
export HOMEPAGE_VERSION

PROJECT=$PROJECT_ID
if [ "$PROJECT" = "" ]; then
    PROJECT=$(gcloud config list --format 'value(core.project)' 2>/dev/null)
fi
export PROJECT

sed \
    -e "s/\${HOMEPAGE_VERSION}/$HOMEPAGE_VERSION/" \
    -e "s/\${PROJECT}/$PROJECT/" \
    migrate.yaml.tmpl
