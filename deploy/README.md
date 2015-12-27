# Setting up the HTTP Load Balancer

1. Create global IP

    $ gcloud compute addresses create www-ianlewis-org --global

1. Create SSL certificates

    $ gcloud compute ssl-certificates create www-ianlewis-org --certificate www.ianlewis.org.crt --private-key www.ianlewis.org.key

1. Create health checks

    $ gcloud compute http-health-checks create homepage-prod-http --host www.ianlewis.org --port <http-port> --request-path=/_status/healthz
    $ gcloud compute https-health-checks create homepage-prod-https --host www.ianlewis.org --port <https-port> --request-path=/_status/healthz

1. Create named ports

    $ gcloud compute instance-groups set-named-ports <gke-instance-group> --named-ports homepage-prod-http:<http-port>,homepage-prod-https:<https-port>

1. Create backend services

    $ gcloud compute backend-services create homepage-prod-http --http-health-checks homepage-prod-http --port-name homepage-prod-http --protocol HTTP
    $ gcloud compute backend-services add-backend homepage-prod-http --instance-group <gke-instance-group> --balancing-mode RATE --max-rate-per-instance 10

    $ gcloud compute backend-services create homepage-prod-https --https-health-checks homepage-prod-https --port-name homepage-prod-https --protocol HTTPS
    $ gcloud compute backend-services add-backend homepage-prod-https --instance-group <gke-instance-group> --balancing-mode RATE --max-rate-per-instance 10

1. Create URL maps

    $ gcloud compute url-maps create homepage-prod-http --default-service homepage-prod-http
    $ gcloud compute url-maps create homepage-prod-https --default-service homepage-prod-https

1. Create target proxies

    $ gcloud compute target-http-proxies create homepage-prod-http --url-map homepage-prod-http
    $ gcloud compute target-https-proxies create homepage-prod-https --url-map homepage-prod-https --ssl-certificate www-ianlewis-org

1. Create forwarding rules

   The static ip address created earlier must be entered by address (not by name)

    $ gcloud compute forwarding-rules create homepage-prod-http --global --address <ip-address> --ip-protocol TCP --port-range 80 --target-http-proxy homepage-prod-http
    $ gcloud compute forwarding-rules create homepage-prod-https --global --address <ip-address> --ip-protocol TCP --port-range 443 --target-https-proxy homepage-prod-https
