# Makefile to build aggre_mod and related packages

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')
VERSION=$(shell cat VERSION)

all: dyndns-server

# Build the server for the local architecture
dyndns-server:
	go generate
	CGO_ENABLED=0 go build -o dyndns-server -a -ldflags '-s' -installsuffix cgo .

# Build a docker image for the local architecture
image: dyndns-server 
	docker build -t asia.gcr.io/$(PROJECT)/dyndns-server:$(VERSION) .

push:
	$(SHELL) -ec 'gcloud docker -- push asia.gcr.io/$(PROJECT)/dyndns-server:$(VERSION)'

clean:
	rm -f dyndns-server
