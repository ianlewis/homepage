_SHORT_SHA = $(shell git rev-parse --short HEAD)

.PHONY: deploy-to-staging deploy-to-prod

deploy-to-staging:
	gcloud container builds submit --config=homepage/cloudbuild.yaml --substitutions=_NAMESPACE=staging,SHORT_SHA=$(_SHORT_SHA)

deploy-to-prod:
	gcloud container builds submit --config=homepage/cloudbuild.yaml --substitutions=_NAMESPACE=prod,SHORT_SHA=$(_SHORT_SHA)
