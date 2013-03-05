# -*- coding: utf-8 -*-
from __future__ import print_function
from exhibitionist.toolbox import ExhibitionistRequestHandler

import tornado.web
from exhibitionist.decorators import http_handler
from exhibitionist.mixins.json import JSONMixin
from exhibitionist.mixins.cors import CORSMixin

# this is used to test auto-discovery of http_handlers
# via modules, as well as the JSON and CORS mixins

# expose static files to client
@http_handler(r'/blahldkfj')
class MyJSONView(CORSMixin("CORS"), JSONMixin(callback_arg="cb"),ExhibitionistRequestHandler):
    def get(self, *args, **kwds):
        print(self.request.uri)
        self.write_json(dict(foo="bar"))
