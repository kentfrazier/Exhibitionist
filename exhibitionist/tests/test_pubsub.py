# -*- coding: utf-8 -*-
from __future__ import print_function

from exhibitionist.isubscriber import ISubscriber

from exhibitionist.mixins.pubsub import PubSubMixin
import unittest


class TestPubSub(unittest.TestCase):
    def setUp(self):
        self.pubsub = PubSubMixin()

    def tearDown(self):
        pass

    @staticmethod
    def pick_attr(l, attr):
        return [getattr(x, attr) for x in l]

    def test_sub(self):
        # basic sub
        h = ISubscriber()

        self.pubsub.subscribe(h, "ch1")
        self.assertTrue(h in self.pubsub.list_subs("ch1"))

    def test_resub_no_dupe(self):
        # basic sub
        h = ISubscriber()

        self.pubsub.subscribe(h, "ch1")
        self.pubsub.subscribe(h, "ch1")
        self.assertTrue(h in self.pubsub.list_subs("ch1"))
        self.assertTrue(len(self.pubsub.list_subs("ch1")) == 1)

    def test_sub_multi_channels(self):
        # basic sub
        h = ISubscriber()
        h2 = ISubscriber()
        self.pubsub.subscribe(h, "ch1")
        self.pubsub.subscribe(h, "ch2")
        self.assertTrue(h in self.pubsub.list_subs("ch1"))
        self.assertTrue(h in self.pubsub.list_subs("ch2"))

        self.pubsub.subscribe(h2, "ch1")
        self.pubsub.subscribe(h2, "ch2")
        self.assertTrue(h in self.pubsub.list_subs("ch1"))
        self.assertTrue(h2 in self.pubsub.list_subs("ch1"))
        self.assertTrue(h2 in self.pubsub.list_subs("ch2"))


    def test_unsub(self):
        h = ISubscriber()
        h2 = ISubscriber()

        self.pubsub.subscribe(h, "ch1")
        self.pubsub.subscribe(h2, "ch1")
        self.pubsub.subscribe(h, "ch2")
        self.pubsub.subscribe(h, "ch3")
        self.assertTrue(h in self.pubsub.list_subs("ch1"))
        self.assertTrue(h in self.pubsub.list_subs("ch2"))
        self.assertTrue(h in self.pubsub.list_subs("ch3"))

        # specific ch
        self.pubsub.unsubscribe(h, "ch1")
        self.assertFalse(h in self.pubsub.list_subs("ch1"))
        self.assertTrue(h in self.pubsub.list_subs("ch2"))
        self.assertTrue(h2 in self.pubsub.list_subs("ch1"))


        # specific ch
        self.pubsub.unsubscribe(h)
        self.assertFalse(h in self.pubsub.list_subs("ch1"))
        self.assertFalse(h in self.pubsub.list_subs("ch2"))
        self.assertFalse(h in self.pubsub.list_subs("ch3"))
        self.assertTrue(h2 in self.pubsub.list_subs("ch1"))


    def test_list_channels(self):
        h = ISubscriber()
        h2 = ISubscriber()

        self.pubsub.subscribe(h, "ch1")
        self.assertTrue("ch1" in self.pubsub.list_channels())
        self.assertFalse("ch2" in self.pubsub.list_channels())

        self.pubsub.subscribe(h, "ch2")
        self.assertTrue("ch1" in self.pubsub.list_channels())
        self.assertTrue("ch2" in self.pubsub.list_channels())



