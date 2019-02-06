# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import blog_pb2 as blog__pb2


class BlogStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetPost = channel.unary_unary(
        '/blog.Blog/GetPost',
        request_serializer=blog__pb2.GetPostRequest.SerializeToString,
        response_deserializer=blog__pb2.GetPostReply.FromString,
        )
    self.GetPage = channel.unary_unary(
        '/blog.Blog/GetPage',
        request_serializer=blog__pb2.GetPageRequest.SerializeToString,
        response_deserializer=blog__pb2.GetPageReply.FromString,
        )
    self.GetNumPages = channel.unary_unary(
        '/blog.Blog/GetNumPages',
        request_serializer=blog__pb2.GetNumPagesRequest.SerializeToString,
        response_deserializer=blog__pb2.GetNumPagesReply.FromString,
        )


class BlogServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetPost(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetPage(self, request, context):
    """Returns a page of active(published) blog posts that
    have a pub_date in the past.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetNumPages(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_BlogServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetPost': grpc.unary_unary_rpc_method_handler(
          servicer.GetPost,
          request_deserializer=blog__pb2.GetPostRequest.FromString,
          response_serializer=blog__pb2.GetPostReply.SerializeToString,
      ),
      'GetPage': grpc.unary_unary_rpc_method_handler(
          servicer.GetPage,
          request_deserializer=blog__pb2.GetPageRequest.FromString,
          response_serializer=blog__pb2.GetPageReply.SerializeToString,
      ),
      'GetNumPages': grpc.unary_unary_rpc_method_handler(
          servicer.GetNumPages,
          request_deserializer=blog__pb2.GetNumPagesRequest.FromString,
          response_serializer=blog__pb2.GetNumPagesReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'blog.Blog', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))