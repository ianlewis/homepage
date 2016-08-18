#!/bin/bash -x

# Sets up the DNS, SSL certs, and loadbalancers for my website.
# Requires the Google Cloud SDK and lego

set -e

# Config

# prod
# NAMESPACE=prod
# HOST=ianlewis.org
# ADDRESS_NAME=www-ianlewis-org

# staging
NAMESPACE=staging
HOST=staging.ianlewis.org
ADDRESS_NAME=www-staging-ianlewis-org

# ----------------------

export GCE_PROJECT=ianlewis-org   # used by lego
WWW_HOST=www.${HOST}
API_HOST=api.${HOST}
CERT_FILE=${HOME}/.lego/certificates/${WWW_HOST}.crt
KEY_FILE=${HOME}/.lego/certificates/${WWW_HOST}.key
DNS_ZONE=ianlewis-org

INSTANCE_GROUP=`gcloud compute instance-groups list --regex="gke-ianlewis-org-.*" | tail -n+2 | awk '{ print $1 }'`
INSTANCE_GROUP_TAG=`echo ${INSTANCE_GROUP} | rev | cut -c 7- | rev`-node
HTTP_PORT=`kubectl get service homepage-v3 -o=json --namespace=homepage-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http")].nodePort}'`
HTTPS_PORT=`kubectl get service homepage-v3 -o=json --namespace=homepage-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http2")].nodePort}'`
API_PORT=`kubectl get service ianlewis-api -o=json --namespace=ianlewis-api-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http")].nodePort}'`

gcloud compute addresses create ${ADDRESS_NAME} --global
IP_ADDRESS=`gcloud compute addresses list ${ADDRESS_NAME} | tail -n+2 | awk '{ print $2 }'`

gcloud dns record-sets transaction start --zone=${DNS_ZONE}
gcloud dns record-sets transaction add --zone=${DNS_ZONE} --name ${HOST} --ttl 300 --type A "${IP_ADDRESS}"
gcloud dns record-sets transaction add --zone=${DNS_ZONE} --name ${WWW_HOST} --ttl 300 --type CNAME "${HOST}."
gcloud dns record-sets transaction add --zone=${DNS_ZONE} --name ${API_HOST} --ttl 300 --type CNAME "${HOST}."
gcloud dns record-sets transaction execute --zone=${DNS_ZONE}

# Wait for transaction to finish.
sleep 30

lego --email="ianmlewis@gmail.com" -d ${WWW_HOST} -d ${API_HOST} --dns="gcloud" --accept-tos run

gcloud compute ssl-certificates create ${ADDRESS_NAME} --certificate ${CERT_FILE} --private-key ${KEY_FILE}

gcloud compute http-health-checks create homepage-${NAMESPACE}-http --host ${WWW_HOST} --port ${HTTP_PORT} --request-path=/_status/healthz
gcloud compute https-health-checks create homepage-${NAMESPACE}-https --host ${WWW_HOST} --port ${HTTPS_PORT} --request-path=/_status/healthz
gcloud compute http-health-checks create ianlewis-api-${NAMESPACE}-http --host ${API_HOST} --port ${API_PORT} --request-path=/_status/healthz

gcloud compute instance-groups set-named-ports ${INSTANCE_GROUP} --named-ports homepage-${NAMESPACE}-http:${HTTP_PORT},homepage-${NAMESPACE}-https:${HTTPS_PORT},ianlewis-api-${NAMESPACE}-http:${API_PORT}
gcloud compute firewall-rules create homepage-${NAMESPACE} --allow tcp:${HTTP_PORT},tcp:${HTTPS_PORT} --target-tags ${INSTANCE_GROUP_TAG}
gcloud compute firewall-rules create ianlewis-api-${NAMESPACE} --allow tcp:${API_PORT} --target-tags ${INSTANCE_GROUP_TAG}


gcloud compute backend-services create homepage-${NAMESPACE}-http --http-health-checks homepage-${NAMESPACE}-http --port-name homepage-${NAMESPACE}-http --protocol HTTP
gcloud compute backend-services add-backend homepage-${NAMESPACE}-http --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10

gcloud compute backend-services create homepage-${NAMESPACE}-https --https-health-checks homepage-${NAMESPACE}-https --port-name homepage-${NAMESPACE}-https --protocol HTTPS
gcloud compute backend-services add-backend homepage-${NAMESPACE}-https --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10

gcloud compute backend-services create ianlewis-api-${NAMESPACE}-http --http-health-checks ianlewis-api-${NAMESPACE}-http --port-name ianlewis-api-${NAMESPACE}-http --protocol HTTP
gcloud compute backend-services add-backend ianlewis-api-${NAMESPACE}-http --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10


gcloud compute url-maps create homepage-${NAMESPACE}-http --default-service homepage-${NAMESPACE}-http
gcloud compute url-maps create homepage-${NAMESPACE}-https --default-service homepage-${NAMESPACE}-https
gcloud compute url-maps add-path-matcher homepage-${NAMESPACE}-https --path-matcher-name homepage-${NAMESPACE}-https --new-hosts ${WWW_HOST} --default-service homepage-${NAMESPACE}-https
gcloud compute url-maps add-path-matcher homepage-${NAMESPACE}-https --path-matcher-name ianlewis-api-${NAMESPACE}-http --new-hosts ${API_HOST} --default-service ianlewis-api-${NAMESPACE}-http

gcloud compute target-http-proxies create homepage-${NAMESPACE}-http --url-map homepage-${NAMESPACE}-http
gcloud compute target-https-proxies create homepage-${NAMESPACE}-https --url-map homepage-${NAMESPACE}-https --ssl-certificate ${ADDRESS_NAME}

gcloud compute forwarding-rules create homepage-${NAMESPACE}-http --global --address ${IP_ADDRESS} --ip-protocol TCP --port-range 80 --target-http-proxy homepage-${NAMESPACE}-http
gcloud compute forwarding-rules create homepage-${NAMESPACE}-https --global --address ${IP_ADDRESS} --ip-protocol TCP --port-range 443 --target-https-proxy homepage-${NAMESPACE}-https
