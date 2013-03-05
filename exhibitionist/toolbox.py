# -*- coding: utf-8 -*-
from __future__ import print_function

# This Module collects bits and pieces from all over the place in one namespace
# to reduce import boilerplate.
# Purists may shake their fist and mutter angrily about the evils of 'from x import *'

__all__ = ['HTTPError', 'JSONRequestHandler', 'CORSAllRequestHandler', 'StaticFileHandler',
           'RequestHandler', 'http_handler', 'WSMsg', 'JSONMixin', 'CORSMixin', 'getLogger',
           'UrlDisplay', 'xhtml_escape', 'utf8', 'get_server','ExhibitionistRequestHandler']


# just a messy collection of everything you need
from tornado.web import StaticFileHandler, RequestHandler, HTTPError
from tornado.escape import xhtml_escape, utf8

from exhibitionist.decorators import http_handler, SUPER_CANARY
from exhibitionist.mixins.json import JSONMixin
from exhibitionist.mixins.cors import CORSMixin
from exhibitionist.providers.websocket import WSMsg

from exhibitionist.log import getLogger
from exhibitionist.util.common import UrlDisplay
from exhibitionist import get_server


class ExhibitionistRequestHandler(RequestHandler):
    """
    All views should use a RequestHandler derived from this class.
    This should enable us to introduce new behaviour in the future
    to be availabe with a package upgrade rather then rewriting views.
    Let's hope they remember to call super()

    """
    def __init__(self,*args,**kwds):
        super(ExhibitionistRequestHandler,self).__init__(*args,**kwds)
        # @http_handler checks for this and removes it before calling
        # the method. So we can issue a warning if the user
        # fails to call super().__init__
        setattr(self,SUPER_CANARY,True)


class JSONRequestHandler(JSONMixin(callback_arg="callback"), ExhibitionistRequestHandler):
    pass

class CORSAllRequestHandler(CORSMixin(allowed_domain="*"), JSONRequestHandler):
    pass

