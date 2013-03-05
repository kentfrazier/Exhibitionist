# -*- coding: utf-8 -*-
from __future__ import print_function

CORS_DOMAIN_ATTR = '_cors_domain'


class _CORSMixin(object):
    """
    Internal, don't use this directly.
    """

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', getattr(self,
                                                               CORS_DOMAIN_ATTR))


def CORSMixin(allowed_domain='localhost'):
    """
    a function returning a class, to be used as a mixin for setting appropriate
    CORS (http://www.w3.org/TR/cors/) to enable cross-domain requests.
    the CORS header needs to present on your AJAX endpoints if they are
    on a different domain to that which served the page issuing the AJAX request.

    Usage (allowing access from any domain):

    class MyHandler(CORSMixin(domain="*"), tornado.web.RequestHandler):
        pass

    Note that CORSMixin must appear before tornado.web.RequestHandler
    in the superclass list.

    This is a slight abuse of nomenclature, since a mixin should be a class and
    not a function, but it's nicer then getCORSMixin().

    Provided for convenience , you can set the appropriate headers yourself
    in your handler, implementing some logic based on requests headers (for supporting
    multiple specific domains for example).
    """

    #  returns a class object parametrized by the specified domain
    return type('CORSMixin', (_CORSMixin, ),
                {CORS_DOMAIN_ATTR: allowed_domain})
