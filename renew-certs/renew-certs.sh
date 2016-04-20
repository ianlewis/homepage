#!/bin/bash

# Renews the Let's Encrypt certificate for the website
# and automatically updates the HTTP Load Balancer with
# the new cert.

set -e

# Required environment variables
# GCE_PROJECT: GCP Project id
# EMAIL: Let's Encrypt account email address
# DOMAIN_OPTS: Domains to renew (e.g. -d www.example.com -d www.example2.com
# NAMESPACE: The kubernetes namespace

# Required:
# md5sum

export GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/key.json
export LEGOPATH=/etc/lego/.lego

echo "Authenticating Google SDK"
gcloud auth activate-service-account `cat /etc/secrets/service-account` --key-file /etc/secrets/key.json
gcloud config set project ${GCE_PROJECT}

# Renew the certificates
echo "Renewing certificates..."
if [ -d "${LEGOPATH}" ]; then
    /lego --path=${LEGOPATH} --email=${EMAIL} ${DOMAIN_OPTS} --dns="gcloud" --accept-tos renew
else
    /lego --path=${LEGOPATH} --email=${EMAIL} ${DOMAIN_OPTS} --dns="gcloud" --accept-tos run
fi
echo "Renewal successful."

# Get old cert name
echo "Getting current cert"
OLDCERT=`gcloud compute target-https-proxies describe ${NAMESPACE}-https | grep https://www.googleapis.com/compute/v1/projects/ianlewis-org/global/sslCertificates/ | awk '{print $2}'`
echo "Got current cert: ${OLDCERT}..."

# Determine a certificate name based on a hash of the content.
CERTNAME=homepage-`md5sum -b ${LEGOPATH}/certificates/*.crt | awk '{print $1}'`

echo "Creating new cert: ${CERTNAME}..."
# Create the a new ssl certificate using gcloud
gcloud compute ssl-certificates create ${CERTNAME} --certificate ${LEGOPATH}/certificates/*.crt --private-key ${LEGOPATH}/certificates/*.key

echo "Updating target-https-proxies..."
# Update target-https-proxies to use the new certificate
gcloud compute target-https-proxies update ${NAMESPACE}-https --ssl-certificate ${CERTNAME}
echo "target-https-proxies updated."

# Wait a bit to allow it to propagate.
echo "Waiting for new cert to propagate..."
sleep 60

# Delete the old certificate.
echo "Deleting old certificate: ${OLDCERT}..."
gcloud compute ssl-certificates delete ${OLDCERT}
echo "Done."

# TODO: Revoke old cert?
