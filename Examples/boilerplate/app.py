#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from exhibitionist import get_server
from exhibitionist.util.common import UrlDisplay

import handlers

pjoin = os.path.join
dirname = lambda x: os.path.abspath(os.path.dirname(x))

# tell the server where the templates and static files
# are served from.
# This enables get_template_path() in request handlers
# and {{static_url(filename)}} in templates, if you're using
# the tornado template engine.
STATIC_DIR = pjoin(dirname(__file__), "static")
TEMPLATE_DIR = pjoin(dirname(__file__), "templates")

# Instantiate aserver, register handlers ("views"), and start the server listening
# websockets_enabled=True is the default, You can omit it for brevity
server = get_server(template_path=TEMPLATE_DIR,
                    static_path=STATIC_DIR,
                    websockets_enabled=True).add_handler(handlers).start()

obj = ["foo", "bar", "baz", 1, 2, 3] # the object to be viewed

# get the url of the MainViewHandler view defined in handlers
url = server.get_view_url("MainViewHandler", obj)

# UrlDisplay adapts to the environment in which it is run
# in ipnb you'll get inline html, in ipython-qtconsole it provides a hot link
# and in other environments, a text message with the url
#
# Alternatively, IPNB allows you to install a display hook based on object type
# google "ipython formatters for_type"
# or see:
# http://ipython.org/ipython-doc/stable/api/generated/IPython.core.formatters.html
UrlDisplay(url)

# If websockets are enabled, `server.websocket` becomes available and
# The server.notify_object(channel,payload) can be used push events to all
# clients subscribed to a channel. by convention the objid should be used as the
# channel name.
# See templates/index.html for the javascript that does the subscribing by
# send a "SUB" message over a websocket.
# server.notify_channel(channel,payload) is a closely related methods, that
# allows you to specify an arbitrary channel name. using notify_channel(objid,"foo")
# is the same as notify_object(obj,"foo") if objid corresponds to obj.
# You could for example have all clients register
# on the "all" channel, which would allow you to push a message to all active
# client regardless of the object view they requested.

# server.notify_object(obj,dict(msg_type="GREETING",payload="Hello World!"))


if __name__ == "__main__":
    print("""
    You should be running this in an interactive session. If
    you are, to actually see a view you need to display it as
    the repr() of some object. The url for the view is in
    a variable called "url", which you can open in a browser:

    >>> url

    or try:

    >>> UrlDisplay(url,obj)

    to get a url/HTML view for a dict object created for you. The
    view will display as text/HTML depending on whether you're in
    the terminal, or in IPython-Notebook.

    Please look at the heavily-commented source for 'app.py' for
    help understanding how everything works.
""");