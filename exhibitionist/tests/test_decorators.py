# -*- coding: utf-8 -*-
from __future__ import print_function

###########
# testing #
###########

from exhibitionist.decorators import (http_handler,OBJID_PLACEHOLDER, OBJID_REGEX_GROUP_NAME)

import unittest
from exhibitionist.objectRegistry import ObjectRegistry
from exhibitionist.toolbox import ExhibitionistRequestHandler

context = None # elimiate missing symbol warnings

class TestDecorators(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_marker_substitution(self):
        import re

        @http_handler("#{0}#".format(OBJID_PLACEHOLDER))
        class A(ExhibitionistRequestHandler):
            pass

        self.assertTrue(OBJID_REGEX_GROUP_NAME in re.compile(http_handler.get_route(A)).groupindex)
        self.assertTrue(http_handler.is_decorated_as_http(A))


    def test_view_name(self):
        @http_handler(r"", view_name="blah")
        class A(ExhibitionistRequestHandler):
            pass

        self.assertEqual(http_handler.get_view_name(A), "blah")
        pass

    def test_all_verbs_auto_obj_and_context_injection(self):
        import tornado.web

        registry = ObjectRegistry()

        @http_handler(OBJID_PLACEHOLDER, __registry=registry,__test=True)
        class A(object):
            def get(self, objid, *args, **kwds):
                assert context.object == o
                pass

            def post(self, objid, *args, **kwds):
                assert context.object == o
                pass

            def put(self, objid, *args, **kwds):
                assert context.object == o
                pass

            def delete(self, objid, *args, **kwds):
                assert context.object == o
                pass

            def head(self, objid, *args, **kwds):
                assert context.object == o
                pass

            def options(self, objid, *args, **kwds):
                assert context.object == o
                pass

        for method_name in ['get', 'post', 'put', 'delete', 'head', 'options']:
            o = object()
            objid = registry.register(o)
            handler = A()
            getattr(handler, method_name)(objid=objid)

            try:
                getattr(handler, method_name)(objid="NoSuchObject")
            except tornado.web.HTTPError:
                pass
            else:
                self.fail(method_name)

