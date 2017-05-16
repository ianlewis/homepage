FROM golang:1.8.1-alpine

# Version 2017-04-05
# https://camlistore.org/doc/release/monthly/2017-04-05
RUN \
    apk add --update git && \
    git clone https://github.com/camlistore/camlistore.git && \
    cd camlistore && \
    git checkout 9e34d14ef5 && \
    go run make.go && \
    cp bin/camlistored / && \
    cp bin/camput / && \
    cp bin/camget / && \
    cp bin/camtool / && \
    cd .. && \
    apk del git && \
    rm -rf /var/cache/apk/* && \
    rm -rf camlistore

ENTRYPOINT ["/camlistored"]
