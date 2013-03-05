# -*- coding: utf-8 -*-
from __future__ import print_function

import unittest
from exhibitionist.objectRegistry import ObjectRegistry


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = ObjectRegistry()

    def tearDown(self):
        pass

    def test_repeated_register_same_key(self):
        r = self.registry
        a = (0, 0)
        key = r.register(a)
        self.assertEqual(r.register(a),
                         key) # repeated registration returns same key

    def test_can_register_non_hashable(self):
        r = self.registry
        a = dict()
        key = r.register(a)
        self.assertTrue(key is not None)

    def test_repeated_register_modified_same_key(self):
        r = self.registry
        a = [0, 0]
        key = r.register(a)
        a[1] = 2
        self.assertEqual(r.register(a),
                         key) # repeated registration returns same key

    def test_repeated_register_modified_same_object(self):
        r = self.registry
        a = [0, 0]
        key1 = r.register(a)
        a[1] = 2
        key2 = r.register(a)
        self.assertEqual(id(r.get(key1)), id(r.get(key2))) #

    def test_diff_objects_diff_keys(self):
        r = self.registry
        a = dict()
        b = dict()
        self.assertNotEqual(r.register(a),
                            r.register(b)) # different object get diff hashes

    def test_can_use_weakref(self):
        class A(object):
            pass

        r = self.registry
        a = A()
        key = r.register(a, weak=True)
        self.assertEqual(id(r.get(key)),
                         id(a)) # mutating an object does not alter it's key
        del a
        # import gc
        #
        # gc.collect()
        self.assertEqual(r.get(key), None) # weakrefs are weak

    def test_can_use_hash_prefix(self):
        from exhibitionist.decorators import MIN_OBJID_LEN
        class A(object):
            pass

        # keys shorter then MIN_OBJID_LEN are ignoredI
        r = ObjectRegistry(MIN_OBJID_LEN)
        a = A()
        key = r.register(a)
        for i in range(1, MIN_OBJID_LEN):
            self.assertEqual(r.get(key[:i]), None)

        for i in range(MIN_OBJID_LEN, len(key)):
            self.assertEqual(id(r.get(key[:i])), id(a))


        # make sure collisions are detected
        key = list(r._registry.keys())[0]
        key = key[:-1] + "_"
        r._registry[key] = object()

        self.assertEqual(r.get(key[:-1]), None)







