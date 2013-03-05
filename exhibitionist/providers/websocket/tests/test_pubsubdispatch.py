###########
# testing #
###########
from exhibitionist.isubscriber import ISubscriber

from exhibitionist.pubsubdispatch import PubSubDispatch
import unittest
import time
import threading


class IOLoopMock(object):
    def add_callback(self, callback):
        # import random
        # time.sleep(random.random()*0.05)
        callback()
        pass

    def running(self):
        return True

class Testpubsubdispatch(unittest.TestCase):
    def setUp(self):
        self.pubsubdispatch = PubSubDispatch(IOLoopMock())


    def tearDown(self):
        pass

    @staticmethod
    def wait_for_predicate(pred, timeout, interval=None):
        interval = interval or timeout
        waited = 0
        while waited <= timeout:
            if pred():
                return True
            time.sleep(interval)
            waited += interval
        return False

    def test_message_rx_tx(self):
        l = []

        class A(ISubscriber):
            def notify(self,channel, payload):
                l.append(payload)

        self.pubsubdispatch.subscribe(A(), "ch1")
        self.assertEqual(len(l), 0)
        self.pubsubdispatch.publish(channel="ch1", payload="the payload")

        self.wait_for_predicate(lambda: len(l), 1, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), "the payload")

        # and again
        self.pubsubdispatch.publish(channel="ch1", payload="the payload2")
        self.wait_for_predicate(lambda: len(l), 1, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), "the payload2")

        # two receivers
        self.assertEqual(len(l), 0)
        self.pubsubdispatch.subscribe(A(), "ch1")
        self.pubsubdispatch.publish(channel="ch1", payload="the payload3")
        self.wait_for_predicate(lambda: len(l) >= 2, 1, 0.001)
        self.assertEqual(len(l), 2)
        self.assertEqual(l.pop(), "the payload3")
        self.assertEqual(l.pop(), "the payload3")

        # just the registered channels get the messages for a channel
        self.assertEqual(len(l), 0)
        self.pubsubdispatch.subscribe(A(), "ch2")
        self.pubsubdispatch.publish(channel="ch1", payload="the payload4")
        self.wait_for_predicate(lambda: len(l) >= 2, 1, 0.001)
        self.assertEqual(len(l), 2)
        self.assertEqual(l.pop(), "the payload4")
        self.assertEqual(l.pop(), "the payload4")

        self.assertEqual(len(l), 0)
        self.pubsubdispatch.publish(channel="ch2", payload="the payload5")
        self.wait_for_predicate(lambda: len(l) >= 1, 1, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), "the payload5")

    def test_make_sure_we_dont_recieve_our_own_message(self):

        l = []

        class A(ISubscriber):
            def notify(self,channel, payload):
                l.append(payload)

        a=A()
        #do
        self.pubsubdispatch.subscribe(a, "ch1")
        self.assertEqual(len(l), 0)
        self.pubsubdispatch.publish(channel="ch1", payload="the payload")

        self.wait_for_predicate(lambda: len(l), 0.2, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), "the payload")

        #don't
        self.pubsubdispatch.publish(channel="ch1", payload="the payload",exclude=a)
        self.wait_for_predicate(lambda: len(l), 0.2, 0.001)
        self.assertEqual(len(l), 0)


    def test_make_sure_we_dont_recieve_our_own_message_multiple_subs(self):
        # make sure the other subscriber does get it, no matter the subscribe order

        l = []

        class A(ISubscriber):
            def notify(self,channel, payload):
                l.append(self)

        a=A()
        b=A()

        #do
        self.pubsubdispatch.subscribe(a, "ch1")
        self.pubsubdispatch.subscribe(b, "ch1")
        self.assertEqual(len(l), 0)

        self.pubsubdispatch.publish(channel="ch1", payload="the payload",exclude=a)
        self.wait_for_predicate(lambda: len(l), 0.2, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), b)

        self.pubsubdispatch.publish(channel="ch1", payload="the payload",exclude=b)
        self.wait_for_predicate(lambda: len(l), 0.2, 0.001)
        self.assertEqual(len(l), 1)
        self.assertEqual(l.pop(), a)