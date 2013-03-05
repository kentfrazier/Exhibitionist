#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function


"""
This exampls has nothing to with objects. It just demonstrates the use
of PubSub using websockets. Each side can subscribe to any channel, and publish
events to a channel. We demonstrate this by having both sides subscribe to a channel
using a callback, and then exchanging PING/PONG messages forever , alternating roles
on each iteration. YOu might want to open your browser's debug console, to see
what's going on.

"""
import codecs

import time
import os

from exhibitionist.isubscriber import ISubscriber
from exhibitionist.toolbox import *

from tornado.template import Template

context = None # eliminate tooling "symbol not found"

logger = getLogger(__name__)


class PingPonger(ISubscriber):
    """
    this class is a callback for incoming websocket messages
    messages going our are send through the notify_channel
    command which queues an event with tornado IOLoop in
    a thread-safe manner
    """
    def __init__(self, pubsub):
        self.pubsub = pubsub
        self.pubsub.subscribe(self, "THE_CHANNEL")

    def notify(self, channel, payload):
        # this gets called in the context of the Exhebition server thread
        logger.info(payload)
        if payload == "PING":
            logger.info("caught ping")
            self.pubsub.publish("THE_CHANNEL", dict(msg_type="PUB",payload="PONG",channel="THE_CHANNEL"),self)

            time.sleep(1.0)
            # if there was an Exhibition server going we could add a callback to
            # the Tornado event loop or run this in a thread. pubsub is thread-safe.
            self.pubsub.publish("THE_CHANNEL",dict(msg_type="PUB",payload="PING",channel="THE_CHANNEL"),self)


pjoin = os.path.join
dirname = lambda x: os.path.abspath(os.path.dirname(x))
STATIC_DIR = pjoin(dirname(__file__), "static")
TEMPLATE_DIR = pjoin(dirname(__file__), "templates")

import handlers
server = get_server(template_path=TEMPLATE_DIR,static_path=STATIC_DIR).\
        add_handler(handlers).start()

pp = PingPonger(server.pubsub) # meow

print("Please open the following url in your browser: " +
      server.get_view_url("PingPongView"))

print("""
Open up the javascript console (for *That* tab), and your log should show be
printing notices periodically, indicating messages being exchanged between
python and the client over websockets.
If You're using chrome, developer tools let's you see websockets frames
as they are passed on the wire, from the network tab.
""");