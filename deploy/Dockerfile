FROM python:2.7.9

RUN apt-get update && apt-get install -y libmysqlclient-dev libmemcached-dev libjpeg-dev zlib1g-dev

RUN mkdir -p /homepage
COPY requirements.txt /homepage/
RUN pip install -r /homepage/requirements.txt

COPY homepage.tar.gz /homepage/
RUN pip install /homepage/homepage.tar.gz

CMD [ "homepage", "start", "--addr", "0.0.0.0", "--port", "8000" ]
