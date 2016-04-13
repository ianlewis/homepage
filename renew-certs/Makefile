# Makefile to build aggre_mod and related packages

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')

all: image

# Build a docker image for the local architecture
image:
	docker build -t renew-certs .
	$(SHELL) -ec 'docker tag renew-certs asia.gcr.io/$(PROJECT)/renew-certs:2'

push:
	$(SHELL) -ec 'gcloud docker push asia.gcr.io/$(PROJECT)/renew-certs:2'
