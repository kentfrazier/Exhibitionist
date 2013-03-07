# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import codecs
import logging

from exhibitionist.toolbox import (getLogger, http_handler, JSONRequestHandler,
                                   CORSMixin, StaticFileHandler,
                                   utf8, HTTPError, xhtml_escape)

context = None # get rid of "symbol missing" squiggles in rope

logger = getLogger(__name__)

# you can use your favorite template engine instead
# tornado engine uses "{{context}}" style placeholders,
# tmpl=Template(str) to construct templates,
# and tmpl.generate(**kwds), to render.
from tornado.template import Template

PROJECT_NAME = "myAwesomeProject"

# This endpoint will be  at http://{server_addr}/myAwesomeProject/{objid}
# JSONRequestHandler is a subclass of tornado's RequestHandler
# with the addition of JSONMixin, providing the write_json()
# method.
@http_handler(r'/%s/{{objid}}' % PROJECT_NAME,foo='bar')
class MainViewHandler(JSONRequestHandler):

    # any custom kwds argument specified via @http_handler
    # will be available in kwds
    def initialize(self,**kwds):
        kwds.get('foo') == 'bar'

    # prepare is called after __init__ is run
    def prepare(self):
        pass

    # get is invoked when the user issues an HTTP GET request, the
    # common case. You can also implement put, post, delete and others
    # similarly. see http://www.tornadoweb.org/documentation/web.html
    # whenever the special marker {{objid}} is included in the route
    # objid is passed as an argument to get, and the associated object
    # itself is available at 'context.object'. if an unrecognized
    # objid is provided, a 404 will be raised automatically.
    def get(self, objid):

        # Instantiate a template object using Template engine
        # This can be moved to prepare() when index.html is stabilized
        # Done like this, changes to the template are reflected
        # on (no-cache) refresh

        tmpl_file = os.path.join(self.get_template_path(),"index.html")
        if not(os.path.isdir(self.get_template_path())):
            # logger.fatal(self.transforms)
            logger.fatal(self._transforms)
            self.set_status(500)
            return self.finish("Template path does not exist")

        with codecs.open(tmpl_file) as f:
            self.tmpl = Template(f.read())

        # validate the object's type to avoid mysterious errors later on
        if not isinstance(context.object, (list,tuple)):
            self.set_status(500)
            return self.finish("Bad object type, expected list or tuple")

        # Tornado makes query parameters available via `get_argument`.
        # Here we handle requests for "/myAwesomeProject/{objid}?format=json".
        # These are usually the AJAX requests issued by the client *after*
        # grabbing the HTML page, below.
        if self.get_argument("format", "").lower() == "json":
            # For this example, the payload for the json data returned
            # is just the string representation of the object.
            payload = unicode(context.object).encode('utf-8', 'replace')

            # write_json will encode the payload as json, and send it
            # to the client.
            #
            # IMPORTANT: the payload must be JSON-Encodable.
            #
            # JSONP is automatically used if a query parameter called "callback"
            # was given, jQuery's default name for jsnop.
            # See CORSMixin if you prefer avoiding JSONP.
            self.write_json(dict(payload=payload))

        # if the client requested "/myAwesomeProject/{objid}"
        # we render the HTMl and send it back to the client
        # this is usually the first request.
        else:
            # The object associated with {objid} is available here
            obj = context.object

            # Get back the url of this view. We embed this in the HTML returned
            # to the client, which uses it to issue AJAX requests back to us.
            # e.g '$.getJSON(api_url + "?format=json")' (javascript)
            # See templates/index.html for the javascript side of things
            api_url = context.get_view_url("MainViewHandler", obj)
            api_url += "?format=json"  # add query parameter to url

            # get the websocket connection url ("ws://server_addr/ws")
            # Also embedded int he client HTML, the client opens a websocket
            # on load, and subscribes to notification on the "channel= {objid}"
            ws_url = context.get_ws_url()
            logger.info(self.static_url("."))
            # render the template , see /templates/index.html

            static_base=self.static_url("")[:-1] # strip trailing slash

            body = self.tmpl.generate(
                                      objid=objid,
                                      api_url=api_url,
                                      ws_url=ws_url,
                                      static_url=self.static_url)

            self.write(body) # send the HTML to client


# This handler demonstrates a different style of doing things
# with unique paths, rather then query parameters as seen above.
# CORSMixin can be used to allow cross-origin requests from FriendlyDomain.com

# Uncomment the decorator to activate this endpoint
#@http_handler(r'/%s/{{objid}}/(?P<parity>odd|even)'% PROJECT_NAME)
class AlternativeHandler(CORSMixin('FriendlyDomain.com'), JSONRequestHandler):
    def __init__(self, *args, **kwds):
        super(AlternativeHandler, self).__init__(*args, **kwds)

    # note the 'parity' arg, corresponding to route regex named capture group
    def get(self, objid, parity):

        # validate the object's type to avoid mysterious errors later on
        if not isinstance(context.object, list):
            raise HTTPError(500, # Server Error status code
                            log_message="bad object type") # to the client

        parity = parity.lower()
        base = 0
        if parity == 'odd':
            base = 1 # just the odd elements
        elif parity == 'even':
            base = 0 # just the even elements
        else:
            raise HTTPError(500, # Server Error status code
                            log_message="bad parity")

        # For this example, the payload for the json data returned
        # is just the string representation of the object.
        payload = context.object[base::2]

        # ensure payload is JSON-Encodable by converting everything to it's utf8 repr
        payload = map(utf8, payload)

        # always escape data which might end up as HTML.
        payload = map(xhtml_escape,
                      map(utf8, payload)) # ensure JSON-Encodable
        self.write_json(dict(payload=payload))


