# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple
import logging
from six import string_types

from exhibitionist.mixins.pubsub import PubSubMixin

import exhibitionist.log

logger = exhibitionist.log.getLogger(__name__, )

class PubSubDispatch(PubSubMixin):
    """Manages a list of subscriptions, and provides methods for publishing message to channels"""
    def __init__(self, ioloop):
        super(PubSubDispatch, self).__init__()
        self.ioloop = ioloop
        logger.debug("PubSubDispatch initialized")

    def publish(self,channel,payload,exclude=None):
        """publish a payload to a channel
        if `exclude` is provided, the subscriber(s) given won't be notified,
        Primarily used to prevent a publisher that is also a subscriber to receive messages.

        Websocket clients that publish messages are always excluded from recieving their own messages.

        :param channel:
        :rtype channel: string
        :param payload:
        :rtype payload: JSON-able object
        :param exclude: callback or sequence of calllbacks to be excluded from notification
        :rtype exclude: ISubscriber or sequence of ISubscribers

        :return: None
        """
        exclude = exclude or tuple()
        if not hasattr(exclude,'__iter__'):
            exclude = [exclude]

        logger.debug("Q-msg: [%s] %s" %(channel,payload))
        try:
            cs = self.list_subs(channel)
            # logger.debug("channels: %s" % cs)
            for c in cs:
                if c in exclude:
                    continue

                try:
                    def callback(c,payload):
                        def cb():
                            # c is ISubscriber
                            c.notify(channel, payload)
                        return cb
                    # logger.debug("Queueing ws send in ioloop")
                    self.ioloop.add_callback(callback(c,payload))
                except IOError as  e: # pragma: no cover
                    logger.debug("ioloop stopped: %s " + str(e)) # pragma: no cover
                    break #TODO, make sure client write can't throw IOError, possibly overloading it
                except Exception as  e: # pragma: no cover
                    logger.debug("Error writing to client: %s: " % str(e)) # pragma: no cover

        except Exception as e: # pragma: no cover
            logger.fatal(str(e)) # pragma: no cover
