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
