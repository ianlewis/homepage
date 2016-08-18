FROM alpine:3.3
MAINTAINER Ian Lewis <ianmlewis@gmail.com>

RUN apk update && apk add --upgrade bash sed && rm -rf /var/cache/apk/*
ADD kubectl /kubectl
ADD gocron /gocron

ENTRYPOINT ["/gocron", "-conf=/conf/crontab"]
