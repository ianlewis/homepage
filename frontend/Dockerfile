FROM debian:jessie 

RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y build-essential
RUN apt-get install -y unzip
RUN apt-get install -y libpcre3-dev 

RUN mkdir -p /tmp/nginx_build

# ngx_pagespeed
RUN wget -O /tmp/nginx_build/ngx_pagespeed.zip https://github.com/pagespeed/ngx_pagespeed/archive/release-1.9.32.10-beta.zip 
RUN cd /tmp/nginx_build && unzip ngx_pagespeed.zip
RUN cd /tmp/nginx_build/ngx_pagespeed-release-1.9.32.10-beta/ && wget https://dl.google.com/dl/page-speed/psol/1.9.32.10.tar.gz && tar xzf 1.9.32.10.tar.gz

RUN apt-get install -y zlib1g-dev

# nginx
RUN cd /tmp/nginx_build && wget http://nginx.org/download/nginx-1.9.5.tar.gz && tar xzf nginx-1.9.5.tar.gz
RUN cd /tmp/nginx_build/nginx-1.9.5 && ./configure --add-module=/tmp/nginx_build/ngx_pagespeed-release-1.9.32.10-beta
RUN cd /tmp/nginx_build/nginx-1.9.5 && make && make install

RUN rm -rf /tmp/nginx_build

ADD nginx.conf /nginx.conf
CMD ["/usr/local/nginx/sbin/nginx", "-c", "/nginx.conf", "-g", "daemon off;"]
