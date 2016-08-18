# Setting up the HTTP Load Balancer

1. Get cluster info

    $ NAMESPACE=prod
    $ WWW_HOST=www.ianlewis.org
    $ API_HOST=api.ianlewis.org
    $ INSTANCE_GROUP=`gcloud compute instance-groups list --regex="gke-ianlewis-org-.*" | tail -n+2 | awk '{ print $1 }'`
    $ HTTP_PORT=`kubectl get service homepage-v3 -o=json --namespace=homepage-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http")].nodePort}'`
    $ HTTPS_PORT=`kubectl get service homepage-v3 -o=json --namespace=homepage-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http2")].nodePort}'`
    $ API_PORT=`kubectl get service ianlewis-api -o=json --namespace=ianlewis-api-${NAMESPACE} -o='jsonpath={.spec.ports[?(@.name=="http")].nodePort}'`

1. Create global IP

    $ gcloud compute addresses create www-ianlewis-org --global

1. Create SSL certificates

    $ gcloud compute ssl-certificates create www-ianlewis-org --certificate www.ianlewis.org.crt --private-key www.ianlewis.org.key

1. Create health checks

    $ gcloud compute http-health-checks create homepage-${NAMESPACE}-http --host www.ianlewis.org --port ${HTTP_PORT} --request-path=/_status/healthz
    $ gcloud compute https-health-checks create homepage-${NAMESPACE}-https --host www.ianlewis.org --port ${HTTPS_PORT} --request-path=/_status/healthz
    $ gcloud compute https-health-checks create ianlewis-api-${NAMESPACE}-http --host api.ianlewis.org --port ${API_PORT} --request-path=/_status/healthz

1. Create named ports

    $ gcloud compute instance-groups set-named-ports ${INSTANCE_GROUP} --named-ports homepage-${NAMESPACE}-http:${HTTP_PORT},homepage-${NAMESPACE}-https:${HTTPS_PORT}

1. Create backend services

    $ gcloud compute backend-services create homepage-${NAMESPACE}-http --http-health-checks homepage-${NAMESPACE}-http --port-name homepage-${NAMESPACE}-http --protocol HTTP
    $ gcloud compute backend-services add-backend homepage-${NAMESPACE}-http --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10

    $ gcloud compute backend-services create homepage-${NAMESPACE}-https --https-health-checks homepage-${NAMESPACE}-https --port-name homepage-${NAMESPACE}-https --protocol HTTPS
    $ gcloud compute backend-services add-backend homepage-${NAMESPACE}-https --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10

    # API is HTTP for now.
    $ gcloud compute backend-services create ianlewis-api-${NAMESPACE}-http --http-health-checks ianlewis-api-${NAMESPACE}-http --port-name ianlewis-api-${NAMESPACE}-http --protocol HTTP
    $ gcloud compute backend-services add-backend ianlewis-api-${NAMESPACE}-http --instance-group ${INSTANCE_GROUP} --balancing-mode RATE --max-rate-per-instance 10

1. Create URL maps

    $ gcloud compute url-maps create homepage-${NAMESPACE}-http --default-service homepage-${NAMESPACE}-http
    $ gcloud compute url-maps create homepage-${NAMESPACE}-https --default-service homepage-${NAMESPACE}-https
    $ gcloud compute url-maps add-path-matcher homepage-${NAMESPACE}-https --path-matcher-name ianlewis-api-${NAMESPACE} --default-service ianlewis-api-${NAMESPACE}-http
    $ gcloud compute url-maps add-host-rule homepage-${NAMESPACE}-https --host=${API_HOST} --path-matcher-name ianlewis-api-${NAMESPACE}-http

1. Create target proxies

    $ gcloud compute target-http-proxies create homepage-${NAMESPACE}-http --url-map homepage-${NAMESPACE}-http
    $ gcloud compute target-https-proxies create homepage-${NAMESPACE}-https --url-map homepage-${NAMESPACE}-https --ssl-certificate www-ianlewis-org

1. Create forwarding rules

   The static ip address created earlier must be entered by address (not by name)

    $ gcloud compute forwarding-rules create homepage-${NAMESPACE}-http --global --address <ip-address> --ip-protocol TCP --port-range 80 --target-http-proxy homepage-${NAMESPACE}-http
    $ gcloud compute forwarding-rules create homepage-${NAMESPACE}-https --global --address <ip-address> --ip-protocol TCP --port-range 443 --target-https-proxy homepage-${NAMESPACE}-https
