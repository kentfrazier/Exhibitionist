# -*- coding: utf-8 -*-
from __future__ import print_function

class ISubscriber(object):
    def notify(self,channel, payload): # pragma: no cover
        raise NotImplemented
