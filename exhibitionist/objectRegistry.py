# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple
import logging
import threading
from hashlib import sha1
import random
import weakref
import six

from exhibitionist.decorators import mlock
import exhibitionist.log

logger = exhibitionist.log.getLogger(__name__)

RegObj = namedtuple("RegObj", "ref objid")


class ObjectRegistry(object):
    def __init__(self,min_objid_len=None):
        from exhibitionist.util.compat import OrderedDict

        self.lock = threading.RLock()
        self._registry = OrderedDict()
        self.nonce = str(random.random()) # unique seed for each run
        self._canary = object() # used internally to signal missing object
        self.min_objid_len = min_objid_len

    def hash_obj(self, obj):
        """Taks a hashable object and returns a key as string"""
        return sha1((str(id(obj)) + self.nonce).encode('utf-8')).hexdigest()

    @mlock
    def register(self, obj, weak=False):
        """
        Stores a weakref to an object, and returns a unique key for future retrieval

        weak - [bool:False] if true will use a weakref to the object
        """
        assert obj is not None

        class Ref(object):
            def __init__(self, obj):
                self.obj = obj

            def __call__(self):
                return self.obj

        objid = self.hash_obj(obj)
        if not objid in self._registry:

            if weak:
                logger.debug("Registering Object (weak) {0}".format(objid))
                ref = weakref.ref(obj)
            else:
                logger.debug("Registering Object {0}".format(objid))
                ref = Ref(obj)
            self._registry[objid] = RegObj(ref=ref, objid=objid)
        else:
            pobj = self.get(objid)
            if id(obj) != id(pobj): # hash collision
                msg = "Hash collision detected when trying to register object."
                logger.fatal(msg)
                raise ValueError(msg)

        return objid

    @mlock
    def get(self, objid):
        """Takes a key and returns an object

        The key should be the retval of  a previous call to register(),
        or a prefix of one at least 8 characters long.
        """

        # TODO: Currently specifying a hash prefix is supported by
        # doing a linear scan, the proper way to do this would be a
        # something like a Trie,
        # Room for improvement if performance ever becomes an
        # issue. tested very reasonably with up to 100000 objects
        # "64k should be enough for everybody"

        assert isinstance(objid, six.string_types)

        if self.min_objid_len and len(objid) < self.min_objid_len:
            return None

        candidate = None
        for k in self._registry:
            if k.startswith(objid):
                if candidate:
                    logger.debug("ambiguous objid specified")
                    return None
                else:
                    candidate = k

        objnd =  self._registry.get(candidate, self._canary)

        if objnd != self._canary:
            obj = objnd.ref()
            if isinstance(objnd.ref, weakref.ref) and obj is None:
                logger.debug("Removing GC'd object from registry")

                del self._registry[objid]  # delete ref to garbage-collected object
            else: # weakref expired
                return obj
