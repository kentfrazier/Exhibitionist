# -*- coding: utf-8 -*-
from __future__ import print_function
import six

from exhibitionist.settings import TORNADO_LOG_FILE

import exhibitionist.decorators as decorators
import exhibitionist.exceptions as exceptions
import exhibitionist.isubscriber as isubscriber
import exhibitionist.log as log
import exhibitionist.objectRegistry as objectRegistry
import exhibitionist.pubsubdispatch as pubsubdispatch
import exhibitionist.server as server
import exhibitionist.settings as settings
import exhibitionist.shared as shared

try:
    from exhibitionist.version import short_version, version
except:
    version = 'unknown'
    short_version = 'unknown'


if TORNADO_LOG_FILE:
    import tornado.options

    tornado.options.options['log_file_prefix'].set(TORNADO_LOG_FILE)
    tornado.options.parse_command_line([])



# Entry point
def get_server(port=None, address='127.0.0.1',
               **kwds):
    """Retrieve an instance of ExhibitionistServer


    :param port: port server should bind do, if unspecified, a port
           will be automatically selected.
    :param address: ip address to bind to, by default localhost.
    :param websockets_enabled: (default: True) whether to enable the
          websockets provider.
    :rtype websockets_enabled: bool
    :param **kwds: all other kwds will be passed to the tornado application
          constructor. In particularm you might find the "static_path"
          and "template_path" settings useful.

    :return: an instance of ExhibitionistServer, you must register
        your handlers with add_handler() and call start() to
        launch the server thread and listen to connections.
    :rtype: ExhibitionistServer
    """
    from exhibitionist.server import ExhibitionistServer
    from exhibitionist.providers.websocket import WebSocketProvider as WSP

    assert port is None or isinstance(port,int), port
    assert isinstance(address,six.string_types), address

    websockets_enabled = kwds.pop('websockets_enabled',True)

    server = ExhibitionistServer(port, address,**kwds)

    if websockets_enabled == True:
        server.register_provider(WSP())
    return server


__all__ = ['get_server',
           'decorators',
           'exceptions',
           'isubscriber',
           'log',
           'objectRegistry',
           'pubsubdispatch',
           'server',
           'settings',
           'shared']