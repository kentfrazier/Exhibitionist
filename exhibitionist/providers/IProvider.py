# -*- coding: utf-8 -*-
from __future__ import print_function

class IProvider(object): # pragma: no cover

    name = None # a unique name for the provider

    def register_with_server(self,server):
        """
        will be called by server when the provider is registered
        enables the provider to get a reference to a the server instance
        and register http handlers with it.
        """
        self.server = server # save the server for later
        raise NotImplementedError

    def subscribe(self,h):
        """register handlers with the provider/server

        h is guaranteed to gave self.is_handler(h) True
        The provider can do some private initialization,
        or it can register the handlers with the server.

        This is suitable when the handlers are provided by the
        user rather then bundled with the provider, so
        the handlers are not known beforehand, but are
        provided via a call to add_handler.

        """
        raise NotImplementedError

    def is_handler(self,h):
        """predicate for handlers handled by this provider

        when server.add_handler is called with a namespace, all symbols
        are filteres through provider predicates to isolate the handlers.
        any handler for which the predicate returns True, will result in
        a call to subscribe, with the object as an argument
        """
        raise NotImplementedError

    def populate_context(self,context):
        """context is available to all request handlers in thread

        invoked when the server starts up, and attribute you put on context
        will be available to request handlers.
        """
        raise NotImplementedError

    def stop(self):
        """invoked right before the server thread stops"""
        raise NotImplementedError