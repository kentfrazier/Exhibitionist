# -*- coding: utf-8 -*-
from __future__ import print_function

from tornado.escape import json_encode

JSON_CB_ATTR = '_callback_name'


class _JSONMixin(object):
    """
    Internal. Don't use this directly
    """

    def write_json(self, d):
        self.set_header('Content-Type', 'application/json')

        body = json_encode(d)

        # supported, but the view should set the CORS header, so straight json works
        canary = object()
        callback = self.get_argument(getattr(self, JSON_CB_ATTR),
                                     default=canary, strip=True)

        if callback != canary:
            self.set_header('Content-Type', 'text/javascript')
            body = str(callback) + '(' + body + ')'

        self.write(body)


def JSONMixin(callback_arg='callback'):
    """
    a function returning a class, to be used as a mixin for supporting JSON responses.
    Defines a self.write_json(payload)  method, where payload is the object to be serialized
    as  json and returned to the client.

    If a callback query parameter is present in the request, write_json() will return a JSONP reply.
    The default name of the callback argument is "callback"  (used by jQuery),
    but you can define it's value yourself:

    class MyHandler(JSONMixin(callback_arg="cb"), tornado.web.RequestHandler):
       def get(self):
           ...
           self.write_json(payload)

    Note that JSONMixin must appear before tornado.web.RequestHandler
    in the superclass list.

    This is a slight abuse of nomenclature, since a mixin should be a class and
    not a function, but it's nicer then getJSONMixin().

    """

    return type('JSONMixin', (_JSONMixin, ), {JSON_CB_ATTR: callback_arg})
