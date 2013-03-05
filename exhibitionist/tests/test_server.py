# -*- coding: utf-8 -*-
from __future__ import print_function
import errno

from exhibitionist import get_server
from exhibitionist.exceptions import ExhibitionistError
import unittest

from exhibitionist.objectRegistry import ObjectRegistry
from exhibitionist.toolbox import ExhibitionistRequestHandler

context = None # mute missing symbol warning


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = get_server()


    def tearDown(self):
        if self.server.started_ok:
            self.server.stop()
            self.server.join(5)

    def test_add_handler(self):

        from exhibitionist.decorators import http_handler
        import requests

        # expose static files to client
        @http_handler(r'/')
        class Handler(ExhibitionistRequestHandler):
            def get(self, *args, **kwds):
                self.write("a")

        self.server.add_handler(Handler)
        self.server.start()

        result = requests.get(self.server.get_view_url("Handler")).content
        self.assertEqual(result, b"a")

    def test_websocket_enable_disable(self):
        server = get_server()
        self.assertTrue(hasattr(server.start(), "websocket"))
        server.stop()
        server.join(5)
        server = get_server(websockets_enabled=False)
        self.assertFalse(hasattr(server.start(), "websocket"))
        server.stop()
        server.join(5)

    def test_respect_requested_port(self):
        server = get_server(port=64003).start()
        self.assertEqual(server.port, 64003)

        # dies request port taken
        # logging.info("the next test should fail to bind to 64003")
        try:
            server = get_server(port=64003).start(timeout=0.1)
        except ExhibitionistError as e:
            # self.assertEqual(e.errno, errno.EADDRNOTAVAIL)
            pass
        else:
            self.fail("exception was not raised")

    def test_missing_obj_404(self):
        from exhibitionist.decorators import http_handler
        import requests

        registry = ObjectRegistry()
        basket = []

        @http_handler(r'/{{objid}}', __registry=registry)
        class Handler(ExhibitionistRequestHandler):
            def get(self, *args, **kwds):
                basket.append(context.object)
                self.write("")

        o = object()
        self.server.add_handler(Handler)
        self.server.start()
        self.assertEqual(len(basket), 0)
        url = self.server.get_view_url("Handler", o, __registry=registry)
        url = url[:-1] + "_" # make objid invalid
        r = requests.get(url)
        self.assertEqual(r.status_code, 404)

    def test_can_get_as_objid(self):
        from exhibitionist.decorators import http_handler
        import tornado.web
        import requests

        registry = ObjectRegistry()
        basket = []

        @http_handler(r'/{{objid}}', __registry=registry)
        class Handler(ExhibitionistRequestHandler):
            def get(self, *args, **kwds):
                basket.append(context.object)
                self.write("")

        o = object()
        k = registry.register(o)
        self.server.add_handler(Handler)
        self.server.start()
        self.assertEqual(len(basket), 0)

        url = self.server.get_view_url("Handler", k, __registry=registry)
        r = requests.get(url)
        self.assertEqual(r.status_code, 200)

        self.assertTrue(registry.register(o) in url)
        self.assertTrue(k in url)


    def test_add_obj_handler(self):
        from exhibitionist.decorators import http_handler
        import requests

        registry = ObjectRegistry()
        basket = []

        @http_handler(r'/{{objid}}', __registry=registry)
        class Handler(ExhibitionistRequestHandler):
            def get(self, *args, **kwds):
                basket.append(context.object)
                self.write("")


        class A(object):
            pass

        o = object()
        self.server.add_handler(Handler)
        self.server.start()
        self.assertEqual(len(basket), 0)
        requests.get(
            self.server.get_view_url("Handler", o, __registry=registry))
        self.assertEqual(len(basket), 1)
        self.assertEqual(basket.pop(), o)

        # test weakref reaped
        o = A()
        self.assertEqual(len(basket), 0)
        url = self.server.get_view_url("Handler", o, __registry=registry,
                                       _weakref=True)
        requests.get(url)
        self.assertEqual(len(basket), 1)
        self.assertEqual(basket.pop(), o)
        del o

        r = requests.get(url)
        self.assertEqual(r.status_code, 404)


    def test_add_obj_handler_from_module(self):
        import requests

        import bogus_handlers as handlers

        registry = ObjectRegistry()

        self.server.add_handler(handlers)
        self.server.start()

        url = self.server.get_view_url("MyJSONView", __registry=registry)
        result = requests.get(url)
        body = result.content
        self.assertTrue(b"bar" in body)

        headers = result.headers
        # test JSONMixin
        self.assertEqual(headers["Content-Type"], "application/json")
        # test CORSMixin
        self.assertEqual(headers["Access-Control-Allow-Origin"], "CORS")

        #test JSONP, with custom callback param name
        url = self.server.get_view_url("MyJSONView",
                                       __registry=registry) + "?cb=?"

        result = requests.get(url)
        headers = result.headers
        self.assertEqual(headers["Content-Type"], 'text/javascript')


    def test_can_only_add_providers_before_server_start(self):
        self.server.start()._ensure_up()
        try:
            self.server.register_provider(object())
        except ExhibitionistError:
            pass
        else:
            self.fail("Didn't catch attempt to register provider after start")

    def test_can_only_add_handlers_before_server_start(self):
        self.server.start()._ensure_up()
        try:
            self.server.add_handler(object())
        except Exception:
            pass
        else:
            self.fail("Didn't catch attempt to add handlers after server start")

    def test_pure_evil_at_bay(self):

        # make sure requests to a given port are always handled
        # by the server thread that is listening to that port,
        # even having identical routes on different servers.
        # Tornado 2.4.1 doesn't do that if server threads share the IOLoop

        from tornado.web import RequestHandler
        import threading
        import requests
        from exhibitionist.decorators import http_handler

        bucket = set()

        @http_handler("/a",__test=True)
        class H(RequestHandler):
            def __init__(self, *args, **kwds):
                super(H, self).__init__(*args, **kwds)
                self.bucket = bucket

            def get(self):
                self.bucket.add(threading.current_thread().ident)

        servers = []
        try:

            for i in range(10):
                servers.append(get_server().add_handler(H).start())

            for i in range(100):
                requests.get(servers[0].get_view_url("H"))

            self.assertEqual(len(bucket), 1)
        finally:
            for s in servers:
                try:
                    s.stop()
                except:
                    pass


    def test_notify_channel_takes_strings_only(self):
        try:
            self.server.notify_channel(object(), "")
        except ValueError:
            pass
        else:
            self.fail("failed to raise exception")

    def test_kwds_in_decorator(self):
        from exhibitionist.decorators import http_handler
        import tornado.web
        import requests

        registry = ObjectRegistry()
        basket = []

        @http_handler(r'/{{objid}}', __registry=registry, myArg='abc')
        class Handler(ExhibitionistRequestHandler):
            def initialize(self, myArg):
                basket.append(myArg)

            def get(self, *args, **kwds):
                self.write("")

        o = object()
        self.server.add_handler(Handler)
        self.server.start()
        self.assertEqual(len(basket), 0)
        requests.get(
            self.server.get_view_url('Handler', o, __registry=registry))
        self.assertEqual(len(basket), 1)
        self.assertEqual(basket.pop(), 'abc')



