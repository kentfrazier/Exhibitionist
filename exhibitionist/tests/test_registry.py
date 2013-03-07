# -*- coding: utf-8 -*-
from __future__ import print_function

import unittest
from exhibitionist.decorators import MIN_OBJID_LEN
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

        # keys shorter then MIN_OBJID_LEN are ignored
        r = ObjectRegistry(MIN_OBJID_LEN)
        a = A()
        key = r.register(a)
        for i in range(1, MIN_OBJID_LEN):
            self.assertEqual(r.get(key[:i]), None)

        for i in range(MIN_OBJID_LEN, len(key)):
            self.assertEqual(id(r.get(key[:i])), id(a))


    def test_return_min_len_key(self):
        def full_id(partial):
            return [x for x in d if x.startswith(partial)][0]
        # start returning keys with len >=1
        # force collisions by registering lots of objects
        r=ObjectRegistry(min_objid_len=1)
        d=r._registry

        objs = [object()]
        oids = [r.register(objs[-1])]



        for i in range(512): # 16**3
            objs.append(object())
            oids.append(r.register(objs[-1]))
            self.assertEqual(r.get(full_id(oids[-1])),objs[-1])

            # make sure we get back the same key, if we reregister
            l = len(d)
            self.assertEqual(oids[-1],r.register(objs[-1]))
            # no change in number of keys
            self.assertEqual(len(d), l)

    def test_return_min_len_key_more(self):
        def full_id(partial):
            return [x for x in d if x.startswith(partial)][0]
        # start returning keys with len >=8 (MIN_OBJID_LEN)
        # force collisions by building keys and shoving them
        # into the registry
        # then reregister same object and make sure
        # we get back an objid which is longer then
        # previous iteration, and that we can get back the object
        # # with it.

        r=ObjectRegistry(min_objid_len=8)
        d=r._registry

        HASH_LEN =len(r.hash_obj(object())) # should be 40 for sha1

        objs = [object()]
        partial = r.register(objs[-1])
        oid = full_id(partial)
        for i in range(8,HASH_LEN):
        # now we've yanked a reference out, let's inject
        # back in with the same (i+1)-prefix
            print(d.keys())
            partial += '_'
            new_oid = partial + oid[i+1:]

            # use the registry to store a reference,
            # then yank it out and reinsert with new_oid
            objs.append(object())
            oid = full_id(r.register(objs[-1]))
            d[new_oid] = d.pop(oid)

        # check that the prefix gets us the original object
        # and that the prefix+_ gets us the new object
        # and that registering the same object, gets us the
        # new id
        #     self.assertEqual(r.get(partial[:-1]), objs[-2])

            self.assertEqual(r.get(partial[:-1]), objs[-2])
            self.assertEqual(r.get(partial), objs[-1])






