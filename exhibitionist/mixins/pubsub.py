# -*- coding: utf-8 -*-
from __future__ import print_function

import threading
from collections import namedtuple

from exhibitionist.decorators import mlock

import exhibitionist.log

logger = exhibitionist.log.getLogger(__name__)

Entry = namedtuple("Entry", "priority sub")

class PubSubMixin(object):
    def __init__(self):
        super(PubSubMixin, self).__init__()
        self.table = dict() # (channel,list((sub,priority))
        self.lock = threading.RLock()

    @mlock
    def subscribe(self, sub, channel, priority=0):
        """
        re-registering a sub with the same key will overwrite the priority value
        parameters:

          channel - must be hashable
          sub - the object associated with the channel
          priority - higher priority means higher priority
        """
        from exhibitionist.isubscriber import ISubscriber
        # There are more efficient ways to do all this
        logger.debug("PubSub Subscribing %s to %s" % (sub, channel))

        assert isinstance(sub, ISubscriber)

        subs = self.table.get(channel, [])
        # logger.debug("PubSub.subscribe: %s" % str(subs))

        for i, h in enumerate(subs):
            if id(h.sub) == id(sub):
                subs.remove(h) # will be reinserted with new priority

        self.table[channel] = self.table.get(channel, []) + [Entry(priority=priority, sub=sub)]

        # sort by descending priority
        self.table[channel].sort(key=lambda x: x.priority, reverse=True)
        # logger.debug("PubSub.subscribe: %s" % self.table.get(channel,[]))

        assert channel in self.table

    @mlock
    def unsubscribe(self, sub, channel=None):
        """
        Unregister a previously registered sub.

        params:
        channel - string or None. if None, sub will be unregistered for all channels
                         if channel is specified, the sub will be removed from the given
                         channel.
        sub - the callable previously registered.

        if the given channel/sub is not current registered, the function Ignores it.
        """
        from six import string_types

        assert isinstance(channel, string_types) or channel is None
        assert (not isinstance(sub, string_types)), "Sub can't be a string, did you get arg order wrong?"

        channels = []
        if channel is None:
            channels = self.table.keys()
        elif channel in self.table:
            channels = [channel]

        for k in list(channels): # loop mutates dict, can't be lazy on py3
            l = [x for x in self.table[k] if x.sub != sub]
            if l:
                self.table[k] = l
            else: # gc empty channels
                logger.debug("removing entry")
                del self.table[k]

    @mlock
    def list_subs(self, channel):
        """
        returns a lists of subs for the specified channel

        """
        # logger.fatal(">list_subs: " + str(self.table.get(channel,[])))
        # logger.fatal(">all: " + str(self.table))
        return [x.sub for x in self.table.get(channel, [])]

    @mlock
    def list_channels(self):
        return self.table.keys()
