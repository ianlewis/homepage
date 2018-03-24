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

COPY . /homepage

RUN virtualenv /venv
RUN rm -rf /homepage/homepage/site_media
RUN /venv/bin/pip install -U setuptools
RUN /venv/bin/pip install -r homepage/requirements.txt
RUN /venv/bin/pip install /homepage
# RUN /homepage/venv/bin/python setup.py sdist
# RUN mv dist/homepage-*.tar.gz dist/homepage.tar.gz

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
# COPY --from=0 /homepage/dist/homepage.tar.gz /tmp/homepage.tar.gz
# RUN pip install /tmp/homepage.tar.gz && \
#         rm -rf /tmp/homepage.tar.gz
    
CMD [ "/venv/bin/homepage", "start", "--addr", "0.0.0.0", "--port", "8080" ]
