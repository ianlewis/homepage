FROM python:2.7.16-slim-stretch

RUN set -x \
        && apt-get update \
        && apt-get install -y \
            virtualenv \
            build-essential \
            default-libmysqlclient-dev \
            libmemcached-dev \
            libjpeg-dev \
            zlib1g-dev

COPY setup.py README.md requirements.txt MANIFEST.in LICENSE AUTHORS /homepage/

# Set the version of the app
RUN virtualenv /venv
RUN /venv/bin/pip install -U setuptools
RUN /venv/bin/pip install -r /homepage/requirements.txt

# Copy homepage after installing dependencies in order to take advantage of cache.
COPY homepage/ /homepage/homepage
RUN rm -rf /homepage/homepage/site_media
RUN set -x \
        && cd /homepage \
        && /venv/bin/python setup.py sdist \
        && mv dist/homepage-*.tar.gz dist/homepage.tar.gz
RUN /venv/bin/pip install /homepage/dist/homepage.tar.gz

FROM python:2.7.16-slim-stretch

# Only install non-dev packages
RUN set -x \
        && apt-get update \
        && apt-get install -y \
            libmariadbclient18 \
            libmemcached11 \
            libjpeg62 \
            zlib1g \
        && rm -rf /var/lib/apt/lists/*
# Copy entire virtualenv (with binary builds) from build container
# virtualenv must be at the same directory where it was built
COPY --from=0 /venv /venv

CMD [ "/venv/bin/homepage", "start", "--addr", "0.0.0.0", "--port", "8080" ]
