FROM python:2.7.13

RUN apt-get update && apt-get install -y libmysqlclient-dev libmemcached-dev libjpeg-dev zlib1g-dev

COPY ./dist/homepage.tar.gz /tmp/homepage.tar.gz
RUN pip install /tmp/homepage.tar.gz && \
        rm -rf /tmp/homepage.tar.gz
    
CMD [ "homepage", "start", "--addr", "0.0.0.0", "--port", "8080" ]
