###########
# testing #
###########
# from websocket import create_connection
import nose
from exhibitionist.isubscriber import ISubscriber

from exhibitionist import get_server
from exhibitionist.providers.websocket import WebSocketProvider
from exhibitionist.toolbox import WSMsg


import unittest
import json

from ws4py.client.threadedclient import WebSocketClient


class WSClient(WebSocketClient):
    """utility for testing"""

    def __init__(self, objid, basket, *args, **kwds):
        super(WSClient, self).__init__(*args, **kwds)
        self.basket = basket
        self.objid = objid

    def send(self, payload, binary=False):
        """Transperant json stringify"""
        from six import string_types

        if not isinstance(payload, (string_types, bytearray)):
            payload = json.dumps(payload)
        super(WSClient, self).send(payload, binary)

    def opened(self):
        self.send(WSMsg("SUB", channel=self.objid))

    def closed(self, code, reason=""):
        pass

    def received_message(self, m):
        # print(m.data)
        data = json.loads(m.data.decode('utf-8'))
        self.basket.append(data)


class TestWebsocketBasic(unittest.TestCase):
    def test_creation_and_reg_with_server(self):
        from exhibitionist import get_server

        self.server = get_server(websockets_enabled=True).start()
        assert self.server._ensure_up() == 0
        self.ws_url = self.server.get_view_url('WebSocketEvents')


# noinspection PyUnusedLocal
class TestWebsocket(unittest.TestCase):
    def setUp(self):
        self.server = get_server().start()
        assert self.server._ensure_up() == 0
        self.ws_url = self.server.get_view_url('WebSocketEvents')
        self.o = object()
        self.objid = self.server.registry.register(self.o)

    def tearDown(self):
        self.server.stop()
        self.server.join(5)
        pass

    @staticmethod
    def wait_for_predicate(pred, timeout, interval=None):
        import time

        interval = interval or timeout
        waited = 0
        while waited <= timeout:
            if pred():
                return True
            time.sleep(interval)
            waited += interval
        return False


    def test_pubsub(self):
        raise nose.SkipTest()
        # import threading
        # print threading.enumerate()
        # 1/0
        basket = []
        for i in range(3):
            data = None

            self.o = object()
            objid = self.server.registry.register(self.o)
            ws = WSClient(objid, basket, self.ws_url, protocols=['http-only'])
            ws.connect()
            self.wait_for_predicate(lambda: basket, 1, 0.005)

            data = basket.pop()
            self.assertEqual(  data['msg_type'], 'ACK')
            self.assertEqual(basket, [])
            self.server.notify_object(self.o, WSMsg("foo", payload=i))

            self.wait_for_predicate(lambda: basket, 1, 0.005)
            data = basket.pop()
            self.assertEqual(data['msg_type'], 'foo')
            self.assertEqual(data['payload'], i)
            data = None

            self.o2 = object()
            objid2 = self.server.registry.register(self.o2)
            ws2 = WSClient(objid2, basket, self.ws_url, protocols=['http-only', 'chat'])
            ws2.connect()

            self.wait_for_predicate(lambda: basket, 1, 0.005)
            data = basket.pop()
            self.assertEqual(data['msg_type'], 'ACK', data['payload'])

            data = None
            self.server.notify_object(self.o2, WSMsg("o2", payload=0))
            self.wait_for_predicate(lambda: basket, 1, 0.005)
            data = basket.pop()
            self.assertEqual(data['msg_type'], 'o2')
            self.assertEqual(data['payload'], 0)

            data = None
            self.server.notify_object(self.o, WSMsg("foo", payload=i))
            self.wait_for_predicate(lambda: basket, 1, 0.005)
            data = basket.pop()

            self.assertEqual(data['msg_type'], 'foo')
            self.assertEqual(data['payload'], i)

            self.assertEqual(basket, [])
            ws2.close()
            ws.close()

    def test_2way_pubsub(self):
        raise nose.SkipTest()
        basket = []
        basket2 = []

        data = None

        # have a client connect, and subscribe to a channel
        self.o = object()
        objid = self.server.registry.register(self.o)
        ws = WSClient(objid, basket, self.ws_url, protocols=['http-only'])
        ws.connect()
        self.wait_for_predicate(lambda: basket, 1, 0.005)

        # make sure the client SUB request was ACKnowledged
        data = basket.pop()
        self.assertEqual(data['msg_type'], 'ACK', data['payload'])
        self.assertEqual(basket, [])

        # connected, notify object, and make sure tyhe client receives it
        self.server.notify_object(self.o, WSMsg('foo', payload=33))
        self.wait_for_predicate(lambda: basket, 1, 0.005)
        data = basket.pop()
        self.assertEqual(data['msg_type'], 'foo')
        self.assertEqual(data['payload'], 33)
        self.assertEqual(basket, [])

        data = None

        class A(ISubscriber):
            def notify(self, channel, payload):
                basket2.append( payload)

        # register another subscriber, this time a python, rather then
        # a websocket callback.
        # and publish a message to the channel from the web socket client
        a = A()

        self.server.pubsub.subscribe(a, 'chan')
        ws.send(WSMsg('PUB', payload='m_data', channel='chan'))

        self.wait_for_predicate(lambda: len(basket2)>=1, 1, 0.005)
        self.assertEqual(len(basket2),1)

        self.assertEqual(basket2.pop(), 'm_data')

        ws.close()


    def test_clear_sub_on_close(self):
        raise nose.SkipTest()
        import time

        basket = []

        self.o = object()
        objid = self.server.registry.register(self.o)
        ws = WSClient(objid, basket, self.ws_url, protocols=['http-only', 'chat'])
        ws.connect()

        ws2 = WSClient(objid, basket, self.ws_url, protocols=['http-only', 'chat'])
        ws2.connect()
        self.wait_for_predicate(lambda: len(basket) >= 2, 1, 0.01)

        self.assertTrue(len(basket) == 2)
        data = basket.pop()
        self.assertEqual(data['msg_type'], 'ACK', data['payload'])
        data = basket.pop()
        self.assertEqual(data['msg_type'], 'ACK', data['payload'])

        #
        self.assertTrue(len(basket) == 0)
        self.server.notify_object(self.o, WSMsg("foo", payload=0))
        self.wait_for_predicate(lambda: len(basket) >= 2, 1, 0.01)
        self.assertTrue(len(basket) == 2)

        data = basket.pop()
        self.assertEqual(data['msg_type'], 'foo', data)
        data = basket.pop()
        self.assertEqual(data['msg_type'], 'foo', data)

        lsub = self.server.pubsub.list_subs
        self.assertEqual(len(lsub(objid)), 2)

        ws.close()

        self.wait_for_predicate(lambda: len(lsub(objid)) == 1, 1, 0.01)
        self.assertEqual(len(lsub(objid)), 1)

        ws2.close()

        self.wait_for_predicate(lambda: len(lsub(objid)) == 0, 1, 0.01)
        self.assertEqual(len(lsub(objid)), 0)

        # reap empty channels
        self.assertEqual(len(self.server.pubsub.list_channels()), 0)

