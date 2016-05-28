#!/bin/bash

# Renews the Let's Encrypt certificate for the website
# and automatically updates the HTTP Load Balancer with
# the new cert.

set -e

# Required environment variables
# GCE_PROJECT: GCP Project id
# EMAIL: Let's Encrypt account email address
# ZONE: The Cloud DNS Zone name
# DOMAINS: Space delimited list of domains to renew (e.g. www.example.com www.example2.com test.example.com)
# NAMESPACE: The kubernetes namespace

# Required:
# md5sum

export GOOGLE_SECRETS_PATH=/etc/secrets/google
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_SECRETS_PATH}/key.json
export LEGO_SECRET_ARCHIVE=/etc/secrets/lego/lego-certs.tar.gz
export LEGOPATH=/etc/lego

echo "Running renewal script"
echo "Project: ${GCE_PROJECT}"
echo "Email: ${EMAIL}"
echo "Zone: ${ZONE}"
echo "Domains: ${DOMAINS}"
echo "Namespace: ${NAMESPACE}"
echo

# Extract LEGO secrets
mkdir -p $LEGOPATH
tar xf $LEGO_SECRET_ARCHIVE -C $LEGOPATH

echo "Authenticating Google SDK"
gcloud auth activate-service-account `cat ${GOOGLE_SECRETS_PATH}/service-account` --key-file ${GOOGLE_APPLICATION_CREDENTIALS}
gcloud config set project ${GCE_PROJECT}

# Cleanup.
EXE_TRANS=""
gcloud dns record-sets transaction start --zone=${ZONE}
for DOMAIN in ${DOMAINS}
do
    DNSDATA=`gcloud dns record-sets list --zone=${ZONE} --type=TXT --name=_acme-challenge.${DOMAIN}. | grep _acme-challenge.${DOMAIN}. | awk '{ print $3 " " $4 }'`
    if [ "${DNSDATA}" != "" ]; then
        DNSARRAY=($DNSDATA)
        TTL=${DNSARRAY[0]}
        DATA=${DNSARRAY[1]}
        gcloud dns record-sets transaction remove ${DATA} --zone=${ZONE} --type=TXT --ttl=${TTL} --name=_acme-challenge.${DOMAIN}.
        EXE_TRANS=1
    fi
done
if [ "${EXE_TRANS}" != "" ]; then
    gcloud dns record-sets transaction execute --zone=${ZONE}
else 
    gcloud dns record-sets transaction abort --zone=${ZONE}
fi

DOMAIN_OPTS=""
for DOMAIN in ${DOMAINS}
do
    DOMAIN_OPTS="${DOMAIN_OPTS} -d ${DOMAIN}"
done

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
OLDCERT=`gcloud compute target-https-proxies describe ${NAMESPACE}-https | grep https://www.googleapis.com/compute/v1/projects/${GCE_PROJECT}/global/sslCertificates/ | awk '{print $2}'`
if [ "${OLDCERT}" != "" ]; then
    echo "Got current cert: ${OLDCERT}..."
else
    echo "No current cert."
fi

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
echo "Waiting 60s for new cert to propagate..."
sleep 60

# Delete the old certificate.
if [ "${OLDCERT}" != "" ]; then
    echo "Deleting old certificate: ${OLDCERT}..."
    gcloud -q compute ssl-certificates delete ${OLDCERT}
fi

echo "Done."
