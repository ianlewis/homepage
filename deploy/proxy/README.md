# nghttpx Reverse Proxy

This directory contains the build info for
the nghttpx reverse proxy.

# Building

First build the nghttpx proxy server as a static binary.
You need to have the necessary build libraries installed. See the
[nghttp2 README](nghttp2/README.rst) for details.

    $ cd nghttp2/
    $ autoreconf -i
    $ automake
    $ autoconf
    $ ./configure --enable-static
    $ make
    $ cd ..

Then build the Docker image.

    $ docker build -t nghttpx .
