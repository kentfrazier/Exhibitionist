# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
from functools import wraps
import threading

from exhibitionist.log import getLogger

logger = getLogger("decorator")

# These are the attribute name used to store
# the decorator supplied values on the class
VIEW_NAME_ATTR = "view_name" # key in dict under self.STORE_UNDER_ATTR
ROUTE_ATTR = "view_route" # key in dict under self.STORE_UNDER_ATTR
OBJECT_ATTR = 'object'
AUTO_OBJ_ATTR = 'auto_obj'
KWDS_ATTR = 'kwds'

# the name of the group/argument used to capture the objid
OBJID_REGEX_GROUP_NAME = 'objid'
# the pat placeholder to be replaced by objid regx
OBJID_PLACEHOLDER = '{{%s}}' % OBJID_REGEX_GROUP_NAME
MIN_OBJID_LEN = 8
OBJID_REGEX = '(?P<{obj_group_name}>[a-z\d]{{{min_len},40}})'.format(
    min_len=MIN_OBJID_LEN,
    obj_group_name=OBJID_REGEX_GROUP_NAME)

GET_REG_OBJ_ATTR = "get_obj_from_registry"
GET_VIEW_ATTR = "get_view_url"
PUBSUB_ATTR = "pubsub"

SUPER_CANARY="canary87969875987895"

class http_handler(object):
    """decorator gor http request handlers

    handlers decoarted with the decrorator can be passed
    into , or auto-discovered by, server.add_handler()
    """

    _handlers = dict()
    _context = threading.local()

    @classmethod
    def get_context(cls):
        return cls._context

    @classmethod
    def get_specs(cls):
        return cls._handlers

    def __init__(self, route, view_name=None, **kwds):
        from exhibitionist.shared import registry

        self.registry = kwds.pop('__registry', registry) # for testing
        self.in_test = kwds.pop("__test",False)
        self.auto_obj = OBJID_PLACEHOLDER in route
        self.route = route.replace(OBJID_PLACEHOLDER, OBJID_REGEX)
        self.view_name = view_name
        self.kwds = kwds

    def prefetch_object(self, this, f, objid, *args, **kwds):
        import tornado.web

        # validate objid format
        # objid = kwds.get(OBJID_REGEX_GROUP_NAME)
        objid = str(objid)[:40]

        o = self.registry.get(objid)
        if o is None:
            raise tornado.web.HTTPError(404, 'No such Object')
        else:
            setattr(self.get_context(), OBJECT_ATTR, o)

        val = f(this, objid, *args, **kwds)

        # release ref to object, to allow weakrefs
        # to be reaped
        setattr(self.get_context(), OBJECT_ATTR, None)
        # should have been put there by ExhibitionitRequestHandler
        # if Init was called

        from exhibitionist.log import getLogger
        if not hasattr(this,SUPER_CANARY):
            if not self.in_test:

                getLogger(__name__).error("RequestHandler did not call super().__init__ ")
        else:
            delattr(this,SUPER_CANARY)


        return val

    def inject_context(self, this, f, *args, **kwargs):
        """inject context into method closure"""
        import six

        if six.PY3:
            f.__globals__['context'] = self.get_context()
        else:
            f.func_globals['context'] = self.get_context()

        return f(this, *args, **kwargs)

    def __call__(self, o):
        from exhibitionist.toolbox import ExhibitionistRequestHandler

        # insist, for future-proofing sake
        if not self.in_test:
            assert issubclass(o, ExhibitionistRequestHandler)

        d = {VIEW_NAME_ATTR: self.view_name or o.__name__,
             ROUTE_ATTR: self.route,
             KWDS_ATTR: self.kwds,
             AUTO_OBJ_ATTR: self.auto_obj}

        self._handlers[o] = d

        # inject context into method's globals()
        for method_name in dir(o):
            import types

            if isinstance(getattr(o, method_name),
                          (types.MethodType, types.FunctionType)):
                @wraps(getattr(o, method_name))
                def wrap(f):
                    return lambda x, *args, **kwds: \
                        self.inject_context(x, f, *args, **kwds)

                setattr(o, method_name, wrap(f=getattr(o,
                                                       method_name)))
                # if the {{objid}} marker was included
            #wrap the method in object fetching magical goodness
        if self.auto_obj:
            # http://www.tornadoweb.org/documentation/web.html
            for method_name in ['get', 'post', 'put', 'delete', 'head',
                                'options']:
                if hasattr(o, method_name) and \
                        isinstance(getattr(o, method_name),
                                   (types.MethodType, types.FunctionType)):
                    @wraps(getattr(o, method_name))
                    def wrap(f):
                        return lambda x, *args, **kwds: \
                            self.prefetch_object(x, f, *args, **kwds)

                    setattr(o, method_name, wrap(f=getattr(o,
                                                           method_name)))

        return o

    @classmethod
    def get_view_name(self, h):
        return self._handlers[h].get(VIEW_NAME_ATTR)

    @classmethod
    def get_auto_obj(self, h):
        return self._handlers[h].get(AUTO_OBJ_ATTR)

    @classmethod
    def get_route(self, h):
        return self._handlers[h].get(ROUTE_ATTR)

    @classmethod
    def get_kwds(self, h):
        return self._handlers[h].get(KWDS_ATTR)

    @classmethod
    def is_decorated_as_http(self, h):
        try:
            return h in self._handlers
        except:
            return False


def mlock(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        with self.lock:
            return f(self, *args, **kwargs)

    return inner
