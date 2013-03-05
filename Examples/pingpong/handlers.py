# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs
import os
import logging

from exhibitionist.toolbox import ( getLogger, http_handler,
                                    JSONRequestHandler, StaticFileHandler,
                                    HTTPError)
context = None # eliminate "symbol not found" warning
logger = getLogger(__name__, logging.INFO)

from tornado.template import Template

@http_handler("/game")
class PingPongView(JSONRequestHandler):
    """ This view provides the HTML to the client
    """
    def get(self):
        #note no leading slash, common cause of errors
        tmpl_file = os.path.join(self.get_template_path(),"index.html")
        tmpl = Template(codecs.open(tmpl_file).read())

        static_base=self.static_url("")[:-1] # strip trailing slash
        result= tmpl.generate(static_base=static_base,
                              ws_url=context.get_ws_url(),
                              static_url=self.static_url)
        self.write(result)
