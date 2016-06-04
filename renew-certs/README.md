# renew-certs

This directory contains a script for the batch job to renew HTTP certificates
from Let's Encrypt. The script is run as a Kubernetes job by the internal
[cron](../deploy/gocron) service.

To renew the certs I use a static binary build of
[lego](https://github.com/xenolf/lego) which is a Let's Encrypt ACME API
client.  I use lego to solve a DNS challenge to renew the certificate
automatically using Google CloudDNS. Lego creates the challenge DNS entries and
performs certificate renewal.

Once the certificate is renewed. The new generated certificate is uploaded as an
ssl-certificate on Google Cloud and I update the HTTP load balancer with the new cert.

See the [renew-certs.sh](renew-certs.sh) script for details.

# Secrets

The renew-certs job requires two secrets google-secrets and lego-certs. The
google-secrets secret is used to authenticate with Google Cloud APIs. It contains
two keys:

1. service-account: Contains the service account email address.
1. key.json: The service account key

The lego-certs secret holds lego account info for Let's Encrypt. It contains
on key:

1. lego-certs.tar.gz: A tar gzipped archive of the lego config directory that can be
   passed to the lego --path option. This is used so that we can renew using the same
   Let's Encrypt account as was used to create the certificate.

Create the secret:

    cd ~/.lego
    tar czf lego-certs.tar.gz *
    kubectl create secret generic lego-certs --from-file=lego-certs.tar.gz
