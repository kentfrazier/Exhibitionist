# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple


import exhibitionist.log
from exhibitionist.providers.IProvider import IProvider

GET_WS_URL_ATTR = "get_ws_url"

logger = exhibitionist.log.getLogger(__name__)

def WSMsg(msg_type,payload=None,**kwds):
    # messages from the client to the server
    d=dict(msg_type=msg_type,payload=payload)
    d.update(kwds)
    return d

class WebSocketProvider(IProvider):
    """

    """
    name = "websocket"

    def __init__(self):
        self.server = None

    def register_with_server(self, server):
        import exhibitionist.providers.websocket.handlers as handlers
        self.server = server

        server.add_handler(handlers)  # register addon's HTTP http_handlers with server

    def stop(self):
        pass

    def populate_context(self,context):
        setattr(context,GET_WS_URL_ATTR,lambda : self.server.get_view_url("WebSocketEvents"))
        # thread

    def subscribe(self, h):
        pass

    def is_handler(self,h):
        # no specific handlers for this provider
        # could define a decorator and a predicate if needed
        return  False

