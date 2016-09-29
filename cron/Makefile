# Makefile to build gocron image

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')
VERSION=$(shell cat VERSION)

all: cron-controller

# Build cron-controller for linux
cron-controller:
	go generate
	CGO_ENABLED=0 GOOS=linux go build -o cron-controller -a -ldflags '-s' -installsuffix cgo .

# Build a docker image for the local architecture
image: cron-controller 
	docker build -t cron-controller .
	$(SHELL) -ec 'docker tag cron-controller asia.gcr.io/$(PROJECT)/cron-controller:$(VERSION)'

push:
	$(SHELL) -ec 'gcloud docker push asia.gcr.io/$(PROJECT)/cron-controller:$(VERSION)'

clean:
	rm -f cron-controller 
