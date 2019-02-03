#:coding=utf-8:

import grpc

from django.conf import settings

from homepage.blog.pb import (
    blog_pb2,
    blog_pb2_grpc,
)

channel = grpc.insecure_channel(settings.BLOG_ADDRESS)
blog_stub = blog_pb2_grpc.BlogStub(channel)
