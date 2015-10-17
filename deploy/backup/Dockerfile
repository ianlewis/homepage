FROM debian:jessie
MAINTAINER Ian Lewis <ianmlewis@gmail.com>

RUN apt-get update

# Install base packages
RUN apt-get install -y python
RUN apt-get install -y wget
RUN apt-get install -y unzip
RUN apt-get install -y bzip2

# Install mysql client
RUN apt-get install -y mysql-client

# Install gsutil
RUN wget https://storage.googleapis.com/pub/gsutil.zip
RUN mkdir -p /opt
RUN unzip gsutil.zip -d /opt

# add || true because if there if we are on the latest version then gsutil
# returns an exit code of 1
RUN /opt/gsutil/gsutil update || true

ADD backup.sh /backup.sh

CMD ["/backup.sh"]
