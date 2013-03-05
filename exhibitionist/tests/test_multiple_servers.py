# -*- coding: utf-8 -*-
from __future__ import print_function

###########
# testing #
###########
import errno
import nose

from exhibitionist import get_server
import unittest

context = None # eliminate missing symbol warnings

class TestMultiServers(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stop_server(self):
        import time
        from random import random

        for i in range(10):
            server = get_server().start()
            self.assertTrue(server.isAlive())
            server.stop()
            server.join(1)
            self.assertFalse(server.isAlive())

    def test_stop_server_releases_port(self):
        import time
        from random import random
        import socket

        for i in range(100):
            server = get_server().start()
            self.assertTrue(server.isAlive())

            # make sure port is taken
            s = socket.socket()
            addr, port = server.address, server.port
            # print(addr,port)
            try:
                s.bind((addr, port))
            except socket.error as e:
                if e.errno != errno.EADDRINUSE:
                    self.fail("excpected EADDRINUSE, got some other error")
            else:
                s.close()
                self.fail("socket was supposed to be taken")

            # stop server and wait
            server.stop()
            server.join(1)
            self.assertFalse(server.isAlive())

            # make sure port is available
            try:
                s.bind((addr, port))
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    self.fail("socket not released after server stop()")
                else:
                    self.fail("couldn't bind to available socket, unknown error")
            else:
                s.close()

    def test_multiple(self):
        """
        Torture test of mutliple server,
        mutliple object, multile client hitting
        servers concurrently,

        """
        # lookes like gevent messes up socket closing
        # this interferes with other tests
        raise nose.SkipTest()
        try:
            import gevent
        except ImportError:
            raise nose.SkipTest("gevent not available")

        from gevent import socket
        import requests
        from exhibitionist.objectRegistry import ObjectRegistry
        from exhibitionist.decorators import http_handler
        import tornado.web
        import threading
        import random

        registry = ObjectRegistry()
        @http_handler(r'/{{objid}}', __registry=registry)
        class Handler(tornado.web.RequestHandler):
            def get(self, *args, **kwds):
                self.write(str(id(context.object)))

        N_SERVERS = 3
        N_CONC_CONNS = 20


        for i in range(10):

            try:
                servers = []
                for i in range(N_SERVERS):
                    servers.append(get_server().add_handler(Handler).start())
                assert len(servers) == N_SERVERS

                urls=[]
                objs=[object() for i in range(N_CONC_CONNS)] # use integers
                for i in range(N_CONC_CONNS): # 50 connections at once
                    o = objs[i]
                    r= random.randint(0, N_SERVERS-1)
                    assert r < N_SERVERS
                    s = servers[r]
                    urls.append(s.get_view_url("Handler", o, __registry=registry))
                assert len(urls) == len(objs)
                jobs = [gevent.spawn(requests.get, url) for url in urls]
                gevent.joinall(jobs, timeout=5)

                for i,r in enumerate(jobs):
                    r =r.value
                    self.assertTrue(str(id(objs[i])) == r.content)

            finally:
                for s in servers:
                    try:
                        s.stop()
                    except:
                        pass



