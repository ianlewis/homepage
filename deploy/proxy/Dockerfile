FROM debian:jessie

RUN apt-get update && apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
	&& rm -rf /var/lib/apt/lists/*

RUN buildDeps='g++ libc6-dev make libev-dev libssl-dev zlib1g-dev pkg-config' \
    runDeps='libev4 libssl1.0.0 zlib1g' \
    && set -x \
    && apt-get update && apt-get install -y openssl $buildDeps --no-install-recommends \
    && mkdir -p /usr/src/nghttp2 \
    && curl -sSL "https://github.com/tatsuhiro-t/nghttp2/releases/download/v1.3.4/nghttp2-1.3.4.tar.gz" -o nghttp2.tar.gz \
    && tar -xzf nghttp2.tar.gz -C /usr/src/nghttp2 --strip-components=1 \
    && rm nghttp2.tar.gz \
    && cd /usr/src/nghttp2 && ./configure && cd / \
    && make -C /usr/src/nghttp2 \
    && make -C /usr/src/nghttp2 install \
    && rm -r /usr/src/nghttp2 \
    && apt-get purge -y --auto-remove $buildDeps \
    && apt-get install -y $runDeps \
    && rm -rf /var/lib/apt/lists/*

CMD ["nghttpx", "--backend=127.0.0.1,8001", "--strip-incoming-x-forwarded-for", "--add-x-forwarded-for", "/conf/webfront-key", "/conf/webfront-crt"]
