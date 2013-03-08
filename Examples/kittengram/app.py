#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from math import sin,cos
import numpy as np

from exhibitionist.toolbox import WSMsg,UrlDisplay,get_server
import handlers

SPRITE_SIZE=60 # dimension of single image as rendered in HTML
FRAME_SIZE=600-SPRITE_SIZE-5 # calculare a reasonable framesize

pjoin = os.path.join
dirname = lambda x: os.path.abspath(os.path.dirname(x))
STATIC_DIR = pjoin(dirname(__file__), "static")
TEMPLATE_DIR = pjoin(dirname(__file__), "templates")

server = get_server(template_path=TEMPLATE_DIR,static_path=STATIC_DIR). \
    add_handler(handlers).start()


# generate xy coordinates of a spiral
def spiral(x=FRAME_SIZE/2,y=FRAME_SIZE/2,
           radius=FRAME_SIZE/2, npoints= 100,
           N_ARMS=3):
    def easing(i):
        return i #2-2*(1.0/(1+i**2))

    radius =float(radius)
    x =float(x)
    y =float(y)
    a=N_ARMS*1.0/radius * (2*3.14)

    t=0
    for i in xrange(npoints):
        yield(x+t*cos(a*t),y+t*sin(a*t))
        t = radius*easing(i*1.0/npoints)

obj=list(spiral())
UrlDisplay(server.get_view_url("KittenGram",obj,'cat'))
url=server.get_view_url("KittenGram",obj,'cat')
UrlDisplay(url,str(FRAME_SIZE)+"px")

# open view in browser

# server.notify_object(obj,WSMsg("CMD","play")) # meow
# server.notify_object(obj,WSMsg('CMD','dog')) # I'm a dog person
# server.notify_object(obj,WSMsg("CMD","play")) # woof
# server.notify_object(obj,WSMsg('CMD','cat')) # No, I'm a cat person


# Try opening multiple views of either type in several tabs,
# and conduct a pet orchestra with a "play" message.


# when you're done, shutdown the server to release the socket
# server.stop()


if __name__ == "__main__":
    print("""
    You should be running this in an interactive session. If
    you are, to actually see a view you need to display it as
    the repr() of some object. The url for the view is in
    a variable called "url", which you can open in a browser:

    >>> url

    or try:

    >>> UrlDisplay(url,"600px")

    to get the url/HTML view, depending on whether you're in the
    terminal, or in IPython-Notebook.

    Please look at the source for 'app.py' for more things to try out
    in the interactive prompt.

    This example has some javascript just waiting for you to push
    an event at it.

    Once you have a view loaded, Try these:

    >>> server.notify_object(obj,WSMsg("CMD","play"))
    *meow*
    >>> server.notify_object(obj,WSMsg('CMD','dog'))
    'I'm a dog person'
    >>> server.notify_object(obj,WSMsg("CMD","play"))
    *woof*
    >>> server.notify_object(obj,WSMsg('CMD','cat'))
    'No, I'm a cat person'
""");

