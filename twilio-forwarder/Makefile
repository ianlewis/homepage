# Makefile to build twilio_forwarder and related packages

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')
VERSION=$(shell cat VERSION)

all: twilio-forwarder

# Build the server for the linux architecture
twilio-forwarder:
	go generate
	CGO_ENABLED=0 GOOS=linux go build -o twilio-forwarder -a -ldflags '-s' -installsuffix cgo .

# Build a docker image for the local architecture
image: twilio-forwarder
	docker build -t twilio-forwarder .
	$(SHELL) -ec 'docker tag twilio-forwarder asia.gcr.io/$(PROJECT)/twilio-forwarder:$(VERSION)'

push:
	$(SHELL) -ec 'gcloud docker -- push asia.gcr.io/$(PROJECT)/twilio-forwarder:$(VERSION)'

clean:
	rm -f twilio-forwarder
