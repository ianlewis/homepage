#:coding=utf-8:

import mock

from io import BytesIO

from django.test import (
    SimpleTestCase,
)
from django.test.client import FakePayload

from homepage.wsgi import Cache

__all__ = (
    "CacheWsgiMiddlewareTest",
)

class CacheWsgiMiddlewareTest(SimpleTestCase):
    def get_environ(self, method, path):
        return {
            'REQUEST_METHOD': str(method),
            'PATH_INFO': str(path),
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': str('http'),
            'wsgi.input': FakePayload(b''),
            'wsgi.errors': BytesIO(),
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
        }

    def test_get(self):
        """
        Tests that the Cache-Control header is set
        properly when requesting a static file.
        """
        mockapp = mock.Mock()
        start_response = mock.Mock()

        cache = Cache(mockapp)

        environ = self.get_environ('GET', '/test.txt')
        retval = cache(environ, start_response)

        self.assertEqual(mockapp.call_count, 1)

        args, kwargs = mockapp.call_args
        self.assertEqual(len(args), 2)

        self.assertEqual(args[0], environ, "The first argument is not the wsgi environment.")

        # The second argument is the custom_start_response
        self.assertTrue(callable(args[1]), "The second argument is not callable.")

        # Call the custom_start_response
        retval = args[1]("200 OK", [])

        self.assertEqual(start_response.call_count, 1, "start_response was not called.") 
        self.assertTrue(('Cache-Control', "public, max-age=300") in start_response.call_args[0][1], "Cache-Control header was not set.")
