# Makefile to build aggre_mod and related packages

PROJECT=$(shell gcloud config list project | awk 'FNR==2 { print $$3 }')

all: api-server

# Build the server for the local architecture
api-server:
	CGO_ENABLED=0 go build -o api-server -a -ldflags '-s' -installsuffix cgo .

# Build a docker image for the local architecture
image: api-server 
	docker build -t ianlewis-api .
	$(SHELL) -ec 'docker tag ianlewis-api asia.gcr.io/$(PROJECT)/ianlewis-api:`./api-server -version`'

push:
	$(SHELL) -ec 'gcloud docker push asia.gcr.io/$(PROJECT)/ianlewis-api:`./api-server -version`'

clean:
	rm -f api-server
