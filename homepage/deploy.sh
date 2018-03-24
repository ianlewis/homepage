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

export NGINX_VERSION=1.13.10
envsubst < deploy.yaml.tmpl
