#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import pandas as pd
from pandas.util.testing import makeCustomDataframe as mkdf

from exhibitionist.toolbox import UrlDisplay, get_server

import handlers

# make sure the handlers module is on your python path
# you could just use os.chdir to set the working directory
# to the example root directory.


pjoin = os.path.join
dirname = lambda x: os.path.abspath(os.path.dirname(x))
STATIC_DIR = pjoin(dirname(__file__), "static")
TEMPLATE_DIR = pjoin(dirname(__file__), "templates")

server = get_server(template_path=TEMPLATE_DIR,static_path=STATIC_DIR). \
    add_handler(handlers).start()


def my_repr(df):
    return UrlDisplay(server.get_view_url("dfView", df), "350px")._repr_html_()

# monkey patch pandas to override it's default HTML repr. This could also
# be done # upstream as part of pandas itself.
# a cleaner way would be to use IPNB type-based display hooking
# google "ipython formatters for_type"
# or see
# http://ipython.org/ipython-doc/stable/api/generated/IPython.core.formatters.html

# print fancy link/embedded HTML in qtconsole/ipnb
pd.DataFrame._repr_html_ = my_repr
# now, displaying dataframes in IPython-notebook will open up
# an IFRAME with the grid view

df=mkdf(5000,10)

# now we can display the dataframe from our python prompt
# and view the url or rendered HTML
# >>> df

# try to modify the datdrame inplace, and refresh the grid
# with the bottom left-hand button
# df.ix[0,0]="pooh"

if __name__ == "__main__":
    print("""
    You should be running this in an interactive session. If
    you are, to actually see a view you need to display an object,
    so it's repr() will be displayed. So try:

    >>> df

    to get the url/HTML view, depending on whether you're in the
    terminal, or in IPython-Notebook.

    Please look at the source for 'app.py' for more things to try out
    in the interactive prompt.

    In particular, try modifying the df object:

    >>> df.ix[0,0] = "Pooh"

    and refreshing the grid (refresh button at bottom left corner).

""");
