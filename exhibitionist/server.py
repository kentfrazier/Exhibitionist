# -*- coding: utf-8 -*-
from __future__ import print_function
import os

import threading
import logging
from six.moves import queue
import errno
from tornado.httpserver import HTTPServer
from exhibitionist.pubsubdispatch import PubSubDispatch

import exhibitionist.settings as settings
from exhibitionist.decorators import (http_handler, GET_REG_OBJ_ATTR,
                                      GET_VIEW_ATTR, PUBSUB_ATTR)
from exhibitionist.providers.IProvider import IProvider
from exhibitionist.exceptions import ExhibitionistError
import exhibitionist.log

logger = exhibitionist.log.getLogger(__name__)


class ExhibitionistServer(IProvider, threading.Thread):
    """
    The tornado server thread, and also provides handler
    registration , both HTTP RequestHandlers with tornado
    and other types provided by providers

    all **kwds not consumed by the Server contructor,
    will be passed on as keyword arguments to tornado's
    application constructor. Particular examples are
    "static_path" and "template_path"
    """

    def __init__(self, port=None, address='127.0.0.1',
                 **kwds):
        """
        If port== None, will pick one automatically
        """
        import tornado.web
        import tornado.ioloop

        super(ExhibitionistServer, self).__init__()

        self.name = "ExhibitionistServer Thread"
        self.daemon = True
        self.synq = queue.Queue()
        self.started_ok = False

        # One IOLoop per thread
        # this was a nightmare to debug.
        self.ioloop = tornado.ioloop.IOLoop()

        if kwds.get('static_path') :
            assert os.path.isdir(kwds.get('static_path'))

        if kwds.get('template_path') :
            assert os.path.isdir(kwds.get('template_path'))

        kwds['template_path'] = kwds.get('template_path',
                                         "You_did_not_set_the_template_path")

        # logger.info(kwds)
        self.application = None

        # extra kwds are passed to application as settings
        # self.application.settings.update(kwds)

        self._server = None

        self.tornado_app_settings=kwds

        self.pubsub = PubSubDispatch(self.ioloop)

        self.http_handlers = set()

        self._port_requested = port
        self._address_requested = address
        self._port_used = None
        self._address_used = None

        self.providers = set()

        if kwds.get("__registry"): # for testing
            self.registry = kwds.get("__registry")
        else:
            import exhibitionist.shared

            self.registry = exhibitionist.shared.registry

        # register the provider part of self,
        # with the server part of self.
        self.register_provider(self)


    @staticmethod
    def _discover(pred, or_or_ns):
        """Internal: Takes a predicate + object/namespace, and finds xs for which pred(x)

        :param pred: lambda x: bool
        :param or_or_ns: a python object, including packages/modules
        :rtype : list
        """
        import inspect

        candidates = []

        if inspect.ismodule(or_or_ns):
            # modules and submodules of package
            modules = [or_or_ns]
            modules += [getattr(or_or_ns, x) for x in dir(or_or_ns)
                        if inspect.ismodule(getattr(or_or_ns, x))]
            for m in modules:
                candidates.extend([getattr(m, x) for x in dir(m)])

        candidates.append(or_or_ns)

        return [x for x in candidates if pred(x)]

    #######################
    # The IProvider  interface
    def register_with_server(self, server):
        pass

    def populate_context(self, context):
        setattr(context, GET_VIEW_ATTR, self.get_view_url)
        setattr(context, GET_REG_OBJ_ATTR, self.registry.get)
        setattr(context, PUBSUB_ATTR, self.pubsub)

        pass

    def subscribe(self, h):
        if self.isAlive():
            raise RuntimeError(
                "Registering http handlers after server start is not allowed")

        # exst_names=[x for x in self.http_handlers
        #             if  get_view_name(x) == get_view_name(h)]
        # if exst_names and exst_names[0] != h:
        if h in self.http_handlers:
            raise RuntimeError("view_name collision, "
                               "there's already a handler called %s" %
                               http_handler.get_view_name(h))

        if h not in self.http_handlers:
            tmpl = "Discovered {type} handler '{name}'  tagged with {route}"
            logger.debug(tmpl.format(type='http',
                                     name=http_handler.get_view_name(h),
                                     route=http_handler.get_route(h)))
            self.http_handlers.add(h)

            # update the application http_handlers
            # this allows dynamic addition of http_handlers


    def is_http_handler(self, o):
        from exhibitionist.decorators import http_handler
        import inspect
        import tornado.web

        return (http_handler.is_decorated_as_http(o) and
                (inspect.isclass(o) and issubclass(o,
                                                   tornado.web.RequestHandler)))

    is_handler = is_http_handler

    #######################
    # The server interface
    def register_provider(self, provider):
        import inspect

        if self.started_ok:
            raise ExhibitionistError(
                "can only add providers before server start")

        # todo, refactor in to verify_provider()
        if inspect.isclass(provider):
            raise AssertionError(
                "Provider must be instance, not class. did you forget to add ()?")
        assert isinstance(provider,
                          IProvider), "Provider must be inherit from IProvider"
        assert hasattr(provider, "is_handler")
        assert hasattr(provider, "subscribe")
        self.providers.add(provider)

        provider.register_with_server(self)
        if provider != self: # attach the provider instance as an attribute
            setattr(self, provider.name, provider)

        return self  # fluent

    def add_handler(self, ns_or_h):
        """
        called by user with http_handlers,or modules containing them,
        of whatever type (http, ws). They will be auto-detected
        and registered with the appropriate backend machinery

        may throw RuntimeError if provider refuses to accept new handlers
        (for example, new HTTP handlers after server start)
        """
        if self.started_ok:
            raise ExhibitionistError(
                "can only add handlers before server start")

        for prvdr in self.providers:
            handlers = self._discover(prvdr.is_handler, ns_or_h)
            [prvdr.subscribe(x) for x in
             handlers] # py3 has lazy map, side-effects.

        return self # fluent

    def _register_handlers(self):
        """ register http_handlers with tornado application"""
        from tornado.web import URLSpec,Application

        urlconf = [URLSpec(http_handler.get_route(h), h,
                           name=http_handler.get_view_name(h),
                           kwargs=http_handler.get_kwds(h))
                   for h in self.http_handlers]

        self.application = Application(urlconf,
                                       **self.tornado_app_settings)
        #
        # self.application.add_handlers("", urlconf) # re-register everything


    def get_view_url(self, handler_name, *args, **kwds):
        """Returns a full url for the given view, with given argument

        a wrapper around tornado's reverse_url with some bells and whistles.

        if the handler included the {{objid}} special marker, 'objid'
        must be provide to reverse_url to be inserted into the returned
        url, and args[0] will be interpreted as the object to be viewed.
        If you pass in an object it will automatically be registered
        and the objid substituted into the url, but you can also
        provide an objid for an object previously registered.

        if you want a weakref to be used (to prevent memory leaks) to store
        the object in the object registry ,pass in a kwd argument
        `_weakref=True` when first viewing the argument.
        Note that not all types are supported by weakref.

        :param handler_name: Handler class name, or value of view_name used
            in @http_handler.
        :param obj_or_objid: objid is the return value of a previous call to
            registry.register
        :param args: values to use in unnamed capture groups in route regexp,
            if any.  must match the number and order of groups.
        :param kwds: values to use in named capture groups in route regexp,
            if any   must match the number and and names of groups.

        Throws: IOError if the server thread failed to initialize

        Examples:

        @http_handler("/blah/{{objid}}")
        class A():
           ...

        get_view_url('A',my_object)

        -----------

        @http_handler("/blah/{{objid}}/(\d+)/(?P<an_arg>\w+)")
        class A():
           ...

        get_view_url('A',my_object,12,an_arg="baz")

        -----------

        @http_handler("/blah/(\d+)/(?P<an_arg>\w+)")
        class A():
           ...

        get_view_url('A',12,an_arg="baz")

        -----------
        """
        import exhibitionist.shared as shared
        from tornado import websocket
        from six import string_types

        weak = kwds.pop("_weakref",False)

        if self._ensure_up() != 0:  # make sure the server thread has finished starting up
            raise ExhibitionistError("The server thread failed to start.")

        registry = kwds.pop('__registry', shared.registry)  # for testing
        handler = self.application.named_handlers[handler_name].handler_class

        if args and  http_handler.get_auto_obj(handler):
            obj_or_objid=args[0]
            objid=None

            # let the user provide an objid of registered object
            if  isinstance(obj_or_objid, string_types) and registry.get(obj_or_objid):
                objid = obj_or_objid

            if objid is None:
                objid = registry.register(obj_or_objid,weak=weak)

            if objid is not None:
                args = (objid,) + args[1:]

        path = self.application.reverse_url(handler_name, *args, **kwds)


        # TODO: we special-case WSH here, need to be more general?
        if issubclass(handler, websocket.WebSocketHandler):
            prot = "ws"
        else:
            prot = "http"

        return "{prot}://{addr}:{port}{path}".format(prot=prot,
                                                     addr=self.address,
                                                     port=self.port, path=path)

    def stop(self, block=True, waitfor=0):
        """Initiates a full shutdown of event loop and server.
        if successful, will release the server'socket an the thread will stop,
        Note, that unless stop() is called, the socket used will not be released
        until shutdown, this can act as a leak for sockets.

        :param waitfor: in seconds, time between stopping the server (and providers)
         and calling stop on the event loop.
        """
        import datetime

        def stopCallback2():
            self.ioloop.stop()

        def stopCallback1():
            self.ioloop.add_timeout(datetime.timedelta(seconds=waitfor),
                                    stopCallback2)
        def close_cb(s):
            return lambda : s.stop()

        for p in self.providers:
            if p != self:
                self.ioloop.add_callback(close_cb(p))

        self.ioloop.add_callback(close_cb(self._server))
        self.ioloop.add_callback(stopCallback1)
        if block:
            self.join()
        return self

    def run(self):
        try:
            import socket

            logger.info('Starting Up')

            for p in self.providers:
                p.populate_context(http_handler.get_context())

            self._register_handlers() # register all discovered http_handler with Tornado application

            # extra kwds are passed to application as settings
            # self.application.settings.update(kwds)

            self._server = HTTPServer(self.application, io_loop=self.ioloop)

            port_start = self._port_requested or settings.SERVER_PORT_BASE
            if self._port_requested:
                port_end = self._port_requested + 1
            else:
                port_end = min(65535, port_start + settings.MAX_N_SOCKETS)

            # try and find a free port starting at SERVER_PORT_BASE
            for portnum in range(port_start, port_end):
                try:

                    self._server.listen(portnum,
                                        address=self._address_requested)
                    logger.info('Server listening on port {0}'.format(portnum))
                    self._port_used = portnum
                    self._address_used = self._address_requested

                    self.synq.put(0) # signal successful startup
                    self.ioloop.start()

                    # self.ioloop.close() # despite everything, still throwing fd errors
                    logger.info('Stopped server at {}:{}'.format(self.address,
                                                                 self.port))
                    logger.info('Stopped IOLoop')

                    # not Thread Safe
                    self._port_used = None
                    self._server = None
                    self.application = None

                    return
                except socket.error as  e:
                    if e.errno != errno.EADDRINUSE:  # retry on port used, fail on other problems
                        self.synq.put(e.errno) # pragma: no cover
                        logger.error(str(e)) # pragma: no cover
                        break # pragma: no cover

            logger.error("Couldn't listen on ports: [{},{})".format(port_start,
                                                                    # pragma: no cover
                                                                    port_end)) # pragma: no cover
            self.synq.put(errno.EADDRNOTAVAIL)# pragma: no cover

        except Exception as e: # capture exceptions from daemonic thread to log file
            import traceback as tb

            logger.error(
                "Exception in server thread:\n" + str(e) + str(tb.format_exc()))


    def start(self, block=True, timeout=5):
        """ Start the server socket, bind to a socket and start listening

        Note, that the socket is held until stop() is called, or the main thread exists.
        This can act as a leak, unless stop() is called when the server is no longer needed.

        returns self

        :param timeout: in seconds
        :rtype : ExhibitionistServer
        """
        super(ExhibitionistServer, self).start()
        if block:
            err = self._ensure_up(timeout)
            if err != 0:
                msg = "Server failed to start: %s" % errno.errorcode[err]
                raise ExhibitionistError(msg,errno=err)

        return self # fluent

    def _ensure_up(self, timeout=1):
        """
        we must be sure that the server successfully bound

        :returns : 0 if success, errno <0 if an error occurred
        :rtype : int
        :param timeout: in seconds
        on a addr:port, before returning a url.
        Waits on a signal from the server thread that it is
        ready.

        :rtype : bool
        """

        if self.started_ok:
            return 0
        else:
            try:
                result = errno.EIO # will be returned if error in Queue get
                result = self.synq.get(timeout=timeout)
            except queue.Empty:
                return errno.ETIMEDOUT
            else:
                if result == 0:
                    self.started_ok = True
                    return 0
                else:
                    return result

    def notify_object(self, obj, payload, exclude=None):
        """
        :param obj: any python object
        :param payload: a JSON encodable object to be send to the client
        :param exclude: callback or sequence of calllbacks to be ecluded from notification
        :rtype exclude: ISubscriber or sequence of ISubscribers
        :return:
        """
        objid = self.registry.register(obj)
        return self.notify_channel(channel=objid, payload=payload,
                                   exclude=exclude)

    def notify_channel(self, channel, payload, exclude=None):
        """

        :param channel: the name of a channel to publish a message on, usually an objid
        :param payload:
        :param exclude: callback or sequence of calllbacks to be ecluded from notification
        :rtype exclude: ISubscriber or sequence of ISubscribers
        :return:
        """
        from six import string_types

        if not isinstance(channel, string_types):
            raise ValueError("Channel must be a string")

        # put message in q to notify the pubsubdispatch Thread of message
        # it will then queue on a send on the ioloop
        self.pubsub.publish(channel=channel, payload=payload,
                            exclude=exclude)

    @property
    def port(self):
        """ None if server not active, listening port otherwise"""
        return self._port_used


    @property
    def address(self):
        """ None if server not active, bound address otherwise"""
        return self._address_used
