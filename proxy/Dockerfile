FROM scratch
ADD nghttp2/src/nghttpx /nghttpx
CMD ["/nghttpx", "--backend=127.0.0.1,8080", "/conf/webfront-key", "/conf/webfront-crt"]
