# Makefile to build aggre_mod and related packages

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')
VERSION=$(shell cat VERSION)

all: gocron

# Build gocron for linux
gocron:
	CGO_ENABLED=0 GOOS=linux go build -o gocron -a -ldflags '-s' -installsuffix cgo .

# Build a docker image for the local architecture
image: gocron
	docker build -t gocron .
	$(SHELL) -ec 'docker tag gocron asia.gcr.io/$(PROJECT)/gocron:$(VERSION)'

push:
	$(SHELL) -ec 'gcloud docker push asia.gcr.io/$(PROJECT)/gocron:$(VERSION)'

clean:
	rm -f gocron
