# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple
import logging
import threading
from hashlib import sha1
import random
import weakref
import six

from exhibitionist.decorators import mlock, MIN_OBJID_LEN
import exhibitionist.log

logger = exhibitionist.log.getLogger(__name__)

RegObj = namedtuple("RegObj", "ref objid")


class ObjectRegistry(object):
    def __init__(self,min_objid_len=MIN_OBJID_LEN,use_short_keys=True):
        from exhibitionist.util.compat import OrderedDict

        self.min_objid_len = min_objid_len
        self.use_short_keys = use_short_keys

        self.lock = threading.RLock()
        # by using an Ordered dict, we can disambiguate
        # shortened oids.
        self._registry = OrderedDict()
        self.nonce = str(random.random()) # unique seed for each run
        self._canary = object() # used internally to signal missing object

        self.HASH_LEN = len(self.hash_obj(object()))

    def hash_obj(self, obj):
        """Taks a hashable object and returns a key as string"""
        s = (str(id(obj)) + self.nonce)

        if six.PY3:
            s = s.encode('utf-8')

        return sha1(s).hexdigest()

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

        # TODO: Better Data Structure
        # find the minimum length unique prefix of this objid

        collided=True
        for i in range(self.min_objid_len,len(objid)+1):
            dupes = [x for x in self._registry if x.startswith(objid[:i])]
            # if we found a unique prefix, or this object is already registered
            # and the only dupe with the prefix len is the same object
            # we're good.
            if not dupes or (len(dupes) == 1 and objid == dupes[0]):
                collided=False
                break

        if collided:
            msg = "Hash collision detected when trying to register object."
            logger.fatal(msg)
            raise ValueError(msg)


        # we're good
        if weak:
            logger.debug("Registering Object (weak) {0}".format(objid))
            ref = weakref.ref(obj)
        else:
            logger.debug("Registering Object {0}".format(objid))
            ref = Ref(obj)
        self._registry[objid] = RegObj(ref=ref, objid=objid)

        if not self.use_short_keys:
            i=len(objid)

        return objid[:i]


    @mlock
    def get(self, objid):
        """Takes a key and returns an object

        The key should be the retval of  a previous call to register(),
        or a prefix of one at least min_obj_id(=8) characters long.
        """

        # TODO: Future refactor
        # Do we need current fixed length objids?
        # we return the minimal-len unique prefix, that means,
        # if there was a collision (somewhat unlikely) we'd have
        # two objects whose extent (published) objid differs
        # by one suffix character (e.g ABC and ABCD).
        # good enough for now.

        # TODO: Better Data Structure
        # get via hash prefix is supported with linear scan, we can do better
        #
        # Room for improvement if performance ever becomes an
        # issue. tested very reasonably with up to 100000 objects
        # "64k should be enough for everybody"

        assert isinstance(objid, six.string_types)

        if (self.min_objid_len and len(objid) < self.min_objid_len) or\
                (not self.use_short_keys and len(objid) < self.HASH_LEN) :
            return None

        if objid not in self._registry:
            for k in self._registry:
                if k.startswith(objid):
                    objid = k
                    break

        objnd =  self._registry.get(objid, self._canary)

        if objnd != self._canary:
            obj = objnd.ref()
            if isinstance(objnd.ref, weakref.ref) and obj is None:
                logger.debug("Removing GC'd object from registry")

                del self._registry[objid]  # delete ref to garbage-collected object
            else: # weakref expired
                return obj
