FROM golang:1.6.3-alpine

RUN \
    apk add --update git && \
    git clone https://github.com/camlistore/camlistore.git && \
    cd camlistore && \
    git checkout 108f4b7 && \
    go run make.go && \
    cp bin/camlistored / && \
    cd .. && \
    apk del git && \
    rm -rf /var/cache/apk/* && \
    rm -rf camlistore

ENTRYPOINT ["/camlistored"]
