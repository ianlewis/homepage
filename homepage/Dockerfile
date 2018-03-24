FROM python:2.7.14-slim-jessie

RUN set -x \
        && apt-get update \
        && apt-get install -y \
            build-essential \
            libmysqlclient-dev \
            libmemcached-dev \
            libjpeg-dev \
            zlib1g-dev

COPY . /homepage

WORKDIR /homepage
RUN rm -rf homepage/site_media
RUN pip install -r requirements.txt
RUN python setup.py sdist
RUN mv dist/homepage-*.tar.gz dist/homepage.tar.gz

FROM python:2.7.14-slim-jessie

RUN set -x \
        && apt-get update \
        && apt-get install -y \
            build-essential \
            libmysqlclient-dev \
            libmemcached-dev \
            libjpeg-dev \
            zlib1g-dev \
        && rm -rf /var/lib/apt/lists/*
COPY --from=0 /homepage/dist/homepage.tar.gz /tmp/homepage.tar.gz
RUN pip install /tmp/homepage.tar.gz && \
        rm -rf /tmp/homepage.tar.gz
    
CMD [ "homepage", "start", "--addr", "0.0.0.0", "--port", "8080" ]
