# Makefile to build nginx image

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')
VERSION=1.13.1-3

all: image

# Build a docker image for the local architecture
image:
	docker build -t nginx .
	$(SHELL) -ec 'docker tag nginx asia.gcr.io/$(PROJECT)/nginx:$(VERSION)'

push:
	$(SHELL) -ec 'gcloud docker -- push asia.gcr.io/$(PROJECT)/nginx:$(VERSION)'
