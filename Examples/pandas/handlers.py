# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs
import os
import logging

from exhibitionist.toolbox import ( getLogger, http_handler,
                                    JSONRequestHandler, StaticFileHandler,
                                    HTTPError)
context = None # eliminate tooling "symbol not found"
logger = getLogger(__name__)

from tornado.template import Template


@http_handler(r'/pandas/df/{{objid}}$', view_name="dfView")
class GetDataFrameView(JSONRequestHandler):
    def prepare(self):
        tmpl_file = os.path.join(self.get_template_path(),"jqgrid_view.html")
        if not(os.path.isdir(self.get_template_path())):
            self.set_status(500)
            self.finish("Template path does not exist")
            return
        with codecs.open(tmpl_file) as f:
            self.tmpl = Template(f.read())


    def get(self, objid):
        import pandas as pd
        # by default the object is placed in self.object
        if not isinstance(context.object, pd.DataFrame):
            raise (HTTPError(500, "Object exists, but is not a dataframe"))

        base = "http://{host}/pandas".format(host=self.request.host)
        body = self.tmpl.generate(api_url=base,
                                  objid=objid,
                                  static_url=self.static_url)

        self.write(body)


@http_handler(r'/pandas/(?P<noun>columns|rows)/{{objid}}$')
class jqGridPandasAjax(JSONRequestHandler):
    def get(self, objid, noun):
        import math
        import pandas as pd
        # logger.info(self.request.arguments)
        def listify(o):
            if not isinstance(o, (list, tuple)):
                o = [o, ]
            return list(o)

        df = context.object # we set @http_handler(obj_attr='the_object')

        if not isinstance(df, pd.DataFrame):
            raise (HTTPError(500, "Object exists, but is not a dataframe"))

        if len(df.columns) == 0:
            cidx_nlevels = 0
        else:
            cidx_nlevels = 1 if not hasattr(df.columns, "levels") else len(df.columns[0])

        if len(df.index) == 0:
            ridx_nlevels = 0
        else:
            ridx_nlevels = 1 if not hasattr(df.index, "levels") else len(df.index[0])

        if noun == "columns":
            def mk_col(index, name, width=80, cssClass="", formatter=None, **kwds):
                d = dict(index=index, name=name,
                         width=width, cssClass=cssClass, formatter=formatter)
                d.update(kwds)
                return d

            if (cidx_nlevels == 0):
                raise (HTTPError(500, "no columns"))

            # fake multirow header for pandas Column MultiIndex as multiple lines of text

            # the name field contains a list of string (possibly singleton)
            # one per level of column index
            if cidx_nlevels == 1:
                cols = [[""] * cidx_nlevels] * ridx_nlevels + map(lambda x: [unicode(x)], list(df.columns))
            else:
                cols = [[""] * cidx_nlevels] * ridx_nlevels + map(lambda x: map(unicode, x), list(df.columns))

            columns = [mk_col(i, name, cssClass="", is_index=i < ridx_nlevels)
                       for i, name in enumerate(cols)]
            payload = dict(columns=columns)
            self.write_json(payload)

        elif noun == "rows":
            # the returned json schema is forced by jqGrid
            rows = int(self.get_argument("rows")) # rows per page
            page = int(self.get_argument("page")) # #page requesed

            offset = ((page - 1) * rows)
            count = rows

            payload = dict(total=int(math.ceil(len(df) // rows)), # total number of pages
                           page=page, # current page number
                           records=len(df)) # total rows in dataframe

            if offset < 0 or count < 0 or offset >= len(df):
                # empty response, probably shouldn't happen, try to recover
                payload.update(dict(rows=[]))
                logger.warn("Bad request: offset:%s count:%s" % (offset, count))
            else:
                count = min(count, len(df) - offset) # num rows to return
                # all data gets converted to string, circumvent
                # the dtypes trap. json can't serialize int64, NaNs, etc
                payload.update(dict(rows=[{i: unicode(data) for i, data in
                                           enumerate(listify(df.index[i]) + list(df.irow(i).tolist()))}
                                          for i in range(offset, offset + count)]))

                # logger.info(payload)
            self.write_json(payload)
