FROM python:2.7.14-slim-jessie

RUN set -x \
        && apt-get update \
        && apt-get install -y \
            virtualenv \
            build-essential \
            libmysqlclient-dev \
            libmemcached-dev \
            libjpeg-dev \
            zlib1g-dev

COPY setup.py README.md requirements.txt MANIFEST.in LICENSE AUTHORS /homepage/
COPY homepage/ /homepage/homepage

# Set the version of the app
RUN virtualenv /venv
RUN rm -rf /homepage/homepage/site_media
RUN /venv/bin/pip install -U setuptools
RUN /venv/bin/pip install -r /homepage/requirements.txt
RUN set -x \
        && cd /homepage \
        && /venv/bin/python setup.py sdist \
        && mv dist/homepage-*.tar.gz dist/homepage.tar.gz
RUN /venv/bin/pip install /homepage/dist/homepage.tar.gz

FROM python:2.7.14-slim-jessie

# Only install non-dev packages
RUN set -x \
        && apt-get update \
        && apt-get install -y \
            libmysqlclient18 \
            libmemcached11 \
            libjpeg62 \
            zlib1g \
        && rm -rf /var/lib/apt/lists/*
# Copy entire virtualenv (with binary builds) from build container
# virtualenv must be at the same directory where it was built
COPY --from=0 /venv /venv

CMD [ "/venv/bin/homepage", "start", "--addr", "0.0.0.0", "--port", "8080" ]