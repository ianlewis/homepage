FROM scratch
# ca-certs are required for outbound HTTP connections.
ADD ca-certificates.crt /etc/ssl/certs/
ADD kubectl /kubectl
ADD gocron /gocron
ENTRYPOINT ["/gocron", "-conf=/conf/crontab"]
