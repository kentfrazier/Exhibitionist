# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import json
import six
from exhibitionist.isubscriber import ISubscriber

from tornado import websocket

from exhibitionist.decorators import http_handler,GET_REG_OBJ_ATTR

import exhibitionist.log
from exhibitionist.toolbox import WSMsg, ExhibitionistRequestHandler

logger = exhibitionist.log.getLogger(__name__)
context = None # dummy symbol

@http_handler(r'/ws$')
class WebSocketEvents(ISubscriber,ExhibitionistRequestHandler, websocket.WebSocketHandler,):
    """Websockets events handler

    Messages going over the websocket from/to the client must be a dict with mandatory
    fields "msg_type" and "payload" fields.

    Defines msg_type(s): "PUB","SUB","ACK","NAK"

    Examples Messages

    dict(msg_type="SUB",channel="ch") - client subscribe request for channel "ch"
    dict(msg_type="PUB",payload="p",channel="ch") -
           clients publish payload "p" to channel "ch"
    dict(msg_type="ACK",payload={message}) - reply from server indicating
        that previous request (PUB or SUB) was successful
    dict(msg_type="ACK",payload={message}) - reply from server indicating
        that previous request (PUB or SUB) failed

    """
    def __init__(self,*args,**kwds):
        super(WebSocketEvents, self).__init__(*args,**kwds)
        self.canary=object()

    # ISubscriber interface
    def notify(self,channel, payload):
        logger.debug('sending to websocket ' + str(payload))
        self.write_message(payload) # WebSocketHandler method

    def open(self, objid=None):
        logger.debug('WebSocket opened')

    def on_message(self, message):
        logger.debug('WSMsg Received: ' + str(message))

        try:
            message = json.loads(message)
        except Exception as  e: # pragma: no cover
            self.write_message(WSMsg(msg_type="NAK",payload="Malformed payload"))
            logger.error(str(e))
            return
        try:
            message['msg_type']
        except Exception as  e: # pragma: no cover
            self.write_message(WSMsg(msg_type="NAK",payload="Message must have 'msg_type' field"))
            # logger.error(str(e))
            return

        try:
            if message.get("msg_type") == "SUB":
                channel = message.get("channel")
                if not channel:
                    self.write_message(WSMsg(msg_type="NAK",payload="missing/invalid channel field"))
                else:
                    context.pubsub.subscribe(self,channel)
                    self.write_message(WSMsg(msg_type="ACK",payload=message))

            elif message.get("msg_type") == "PUB":
                channel = message.get("channel")
                payload = message.get("payload")
                if channel is None:
                    self.write_message(WSMsg(msg_type="NAK",payload="missing channel field"))
                if payload is None:
                    self.write_message(WSMsg(msg_type="NAK",payload="missing payload"))
                else:
                    self.write_message(WSMsg(msg_type="ACK",payload=message))
                    context.pubsub.publish(six.text_type(channel), payload,self)

        except Exception as  e: # pragma: no cover
            self.write_message(WSMsg(msg_type="NAK",payload="An error has occured"))
            logger.error(str(e))
            return

    def on_close(self):
        # unregister client from pubsub
        context.pubsub.unsubscribe(self)
        logger.debug('WebSocket closed')
