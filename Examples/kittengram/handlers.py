# from exhibitionist.toolbox import  http_handler,JSONRequestHandler,Template
import os
import codecs
import threading
from exhibitionist.toolbox import *

from tornado.template import Template

context = None # lose the warnings

@http_handler(r'/numpy/{{objid}}/(?P<animal>cat|dog)')
class KittenGram(JSONRequestHandler):
# prepare is called after __init__ is run
    def prepare(self):
        tmpl_file = os.path.join(self.get_template_path(),"index.html")
        if not(os.path.isdir(self.get_template_path())):
            self.set_status(500)
            return self.finish("Template path does not exist")
        with codecs.open(tmpl_file) as f:
            self.tmpl = Template(f.read())

    def get(self, objid, animal):
        if self.get_argument("format", "").lower() == "json":
            self.write_json(context.object)
        else:
            api_url = context.get_view_url("KittenGram", context.object, animal)
            ws_url = context.get_ws_url()
            self.write(self.tmpl.generate(objid=objid,
                                          api_url=api_url + '?format=json',
                                          ws_url=ws_url,
                                          animal=animal,
                                          static_url=self.static_url))
