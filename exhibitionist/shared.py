# -*- coding: utf-8 -*-
from __future__ import print_function

# Package-wide data structure instances live here.

# The objid: object  registry
# this is used by the @route decorator
from exhibitionist.objectRegistry import ObjectRegistry
from exhibitionist.decorators import MIN_OBJID_LEN

__all__=['registry']

# Single Thread-Safe registry, used by all servers.
registry = ObjectRegistry(min_objid_len=MIN_OBJID_LEN,
                          use_short_keys=True)

