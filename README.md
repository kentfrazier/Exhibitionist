Exhibitionist
=======

[![Build Status](https://travis-ci.org/Exhibitionist/Exhibitionist.png?branch=master)](https://travis-ci.org/Exhibitionist/Exhibitionist)

Exhibitionist is a Python library that let's you build tiny web-apps which serve as
views for live python objects in your favorite python shell.
It's built on top of [Tornado](http://www.tornadoweb.org/), so you can do
everything it allows you to do. see Tornado's [overview](http://www.tornadoweb.org/documentation/overview.html)
for examples of what's possible,.

o get started with, the "hello world"
example takes about 10 lines.

If you want to create fully interactive views of python objects using HTML and
leveraging javascript libraries such as [d3.js](http://d3js.org) or your favorite grid/charting
library, exhibitionist allows you to do that succinctly in a way that closely
follows modern web app development practices, in both spirit and process.

The resulting views are available as urls served from a local server and are viewable directly in the browser.  Users of [IPython-notebook](http://gituhb.com/ipython/ipython ) can leverage it's inline display of HTML+Javascript for seamless integration of views into their interactive workflow.

*Features:*

- Out-of-the-box support for two-way message passing between javascript and python using a PubSub mechanism mechanism built on websockets. 
- Use AJAX to dynamically load data, work with large data sets and make things
interactive. do server things on the server and client things on the client. 
- Designed to be a dependency of you library. import it and integrate HTML
views of you classes into your code. or monkey-patch an existing library
with your own UI. It's all good.
- Develop views with your favorite HTML/JS/CSS libraries. Everything is supported.
- Examples included as well as a heavily documented skeleton project to get you started.
- Supports Python 2.6+, 3.2+.
- Tested on linux, reports (and fixes) for other OS's welcome.
- Unit-tests. Coverage. yep
- BSD-licensed, go crazy.
- Repo available on github:  [http://github.com/Exhibitionist/Exhibitionist](http://github.com/Exhibitionist/Exhibitionist)

### FAQ

**Got Eyecandy?**

Sure. Here's the "pandas" example showing a [pandas](http://github.com/pydata/pandas)
dataframe using a javascript grid library, [jqGrid](https://github.com/tonytomov/jqGrid)

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/grid.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/grid.png)

**How does it work?**

By launching an in-process web-server (Tornado) in a separate thread, request
handlers gain access to live python objects in your python process without
blocking it.

You write request handlers that get handed the python object to be viewed
and return HTML or JSON (or anything) to the client as needed. You serve static
assets from wherever you put them, and keep all the source (templates,
.js,.css, images) files organized in a directory as you usually would.
The server (python) and the client(javascript) can exchange messages
via websockets. Both sides can be subscribers and/or publishers and 
push messages to "channels".

**Doesn't IPython-Notebook already allow you to do interactive widgets?**

It's hard to tell, but the answer is probably yes, they've been working
on this for a while now. I encourage you to look at:

- [Z callbacks Notebook](https://github.com/ipython/ipython-in-depth/blob/master/notebooks/Z%20Callbacks.ipynb)-  *hint*, markdown cells can contain javascript.
- [discussion on mailing list](http://python.6.n6.nabble.com/Notebook-Interacting-with-JavaScript-Values-td4954983.html)
- [GH issue](https://github.com/ipython/ipython/issues/2802)
- [Another one](https://github.com/ipython/ipython/issues/2518)
- [GH PR](https://github.com/ipython/ipython/pull/1697)
- [presentation on IPNB](http://vimeo.com/53051817)
- [jsplugins repo](https://github.com/ipython/jsplugins)

I did, and after looking at what's available decided I prefer things to
follow web app development practices, without coupling development or use
to the IPython environment. You should use what works best for you, of course.

One Issue to consider is reproducibility, If you use a library that
integrates views into it's core using exhibitionist, You would be able
to see the views on any system that has the library installed. But
you need to be **running** the code, It's a dependency like any other.
So, for example a service like [nbviewer](http://nbviewer.ipython.org/),
won't generally work. afaict, that's no different from the situation
with interactive visualizations in IPython.

It should be possible to use phantomJS to screen-capture images of
dynamic views, but that's not really something that belongs
in exhibitionist. Cool idea, though.

**Doesn't having multiple threads create Thread-Safety issues?**

Yes it does, and in general you'll have to deal with that. Remember that If 
your views are free of side-effects, the worst that can happen is an 
inconsistent view. just hit refresh.

**Why is there no pypi package available?**

It's too early to make a capital-R release. There probably will be.
In the meantime, pip let's you install directly from git repos,
so you can use:

```
pip install git+git://github.com/Exhibitionist/Exhibitionist.git
```

to install the latest git master of Exhibitionist.

**What does hello world look like?**

*Short.*

Copy & paste this into your IPython/python prompt

```python
from exhibitionist.toolbox import *

@http_handler(r'/myView/{{objid}}$')
class ViewAllTheThings(JSONRequestHandler):
    def get(self,objid):
        if self.get_argument("format","") == "json":
            self.write_json(context.object)
        else:
            obj = context.object #  the object associated with objid
            self.write("<br/>".join("<b>{0}</b>:<em>{1}</em>".format(k,v)
                       for k,v in obj.items()))

# instantiate, register,go.
server = get_server().add_handler(ViewAllTheThings).start() 

# the object to be viewed
obj= dict(hello="world")

# get the url for a view+object combination
# you can open this in any browser
view_url=server.get_view_url("ViewAllTheThings",obj)

# display it. Inline HTML if in IPNB.
UrlDisplay(view_url)

# now, let's get the json version
UrlDisplay(view_url+'?format=json')

```

Producing the following screen, in IPython-Notebook:

[![Image](https://raw.github.com/y-p/Exhibitionist/master/misc/shot1.png)](https://raw.github.com/y-p/Exhibitionist/master/misc/shot1.png)

This conciseness is mostly due to using Tornado, Exhibitionist just adds some
extra sugar.

You can visit the url directly in a browser, it should be something like:
```
`http://localhost:port/myView/{some_long_hash}`
```

if you append `?format=json` to it, you'll get JSON data. a client could get
that data with AJAX.

#### Here's what's going on:
1. We import everything we need from `exhibitionist.toolbox`.
2. we use the `@http_handler` **decorator** to define the "route" for this handler
using a regexp. The **special marker** {{objid}} is included in the uri enables
Exhibitionist to perform some magic.
3. We define the ***Request Handler class** is defined,  All your request handlers
must derive from `ExhibitionistRequestHandler` and should call super().__init__ properly.
`JSONRequestHandler` is a subclass of `ExhibitionistRequestHandler` with
the addition of a "write_json()" method for returning json data.
Whenever the client hits a url matching the "route" defined
(e.g. http://server/myView/{some objid}) an instance of `ViewAllTheThings` is created
and the suitable (get/post/put/delete) method is invoked.
4. The get method accepts an **`objid` arg provided by the {{objid}}** marker
included in the route. You can include named capture group in the route regex
to capture other parts of the uri as as method arguments, see tornado docs or
the examples in the repo.
5. The `context` object ( imported from the `toolbox` module) now **magically holds
a reference** to the object associated with objid.
6. we render some HTML based on the object data and send it back to the client
with a call to self_write(). if a `format=json` query parameter is specified,
we send the object to `write_json` to be json-encoded and returned to the client

That's it for the request handler class.

We then instantiate a server, register the handler class and then spawn the
server in a new thread. At this point, the server is listening for requests.

We create an object (a dict) to render using the view, and use the `get_view_url`,
to pair up a specific view ("ViewAllTheThings") with a specific object
(`obj` in this case). the returned url can be opened in any browser, but
we use the UrlDisplay Helper, which takes advantage of IPython to display the
HTML inline if it's available, or displays a url for the user to open in the
browser.

**Where can I see more?**

The `examples/` directory contains several examples:
- 'boilerplate', a heavily documented skeleton project to start your own views with.
- 'pingpong', a project demonstrating the use of PubSub to exchange messages
between server and client using websockets.
- kittengram, a silly example that uses D3 to visualize arrays as pet scatter
plots. websockets are use to trigger javascript mischief in the browser from
python. meow.
- 'pandas', a more complete example that renders [pandas](http://www.github.com/pydata/pandas)
dataframes using a javascript grid widget [jqGrid](https://github.com/tonytomov/jqGrid).
Data is loaded on-demand using AJAX, so even very large dataframes can be
displayed. Even works with multi-index on either axis ftw.

To run them the examples, you should clone the repo, install Exhibitionist using
"python setup.py install", change directory into the `example/{example_name}` directory
so the examples' modules can be imported and paste the code from app.py
into your IPython/python prompt. you should get a url or rendered view
to admire.

**Why Tornado, why not X?**

I actually prototyped this with [Flask](https://github.com/mitsuhiko/flask),
which was awesome. But ultimately, I believe the majority of users would
use this in conjunction with IPython-notebook, which uses tornado, and so
I decided to dovetail dependencies in order to simplify things.

Currently, the library and examples don't directly use tornado's more unique
features such as async handlers, and multiple threads/IOLoops are used for
multiple servers, which is not the way tornado is usually used.
But, Tornado makes for a nice lightweight web framework, and unused
features might not remain so in the future.

**I'm getting 404/500 error codes and I can't see any debug messages**

By default all logging is routed to '/dev/null'.
You need to enable logging and check see if tornado is spitting
out exceptions about what's wrong.
Place a `local_settings.py` under "exhibitionist/" and override the log filename
constants defined in settings.py for both exhibitionist and tornado to gain some
visibility into what's going on. Use "tail -f" when debugging.

Tornado is currently run with debug=False, because it's autoreload
feature can cause unexpected behaviour when files are modified while
working in IPython. You might want to look into turning the back on.
Just be wary of strange hangs.

**what about security?**

This way of doing things (as a full-blown web-app) opens up a whole bunch
of issues, from data being exposed through the server (although it's bound
to localhost only by default) to xss/csrf attacks through data being fed
un-escaped into HTML and other attacks I haven't even heard of.
You should take all the precautions appropriate to your scenario,
and bear in mind that this was written to help make interactive python work
look and feel nicer. Fending off attackers was not a real design concern.


**Any Gotchas?**

- If you're using IP-Notebook, views relying on AJAX to fetch data can't be
"frozen" with [nbviewer] (http://nbviewer.ipython.org/), you'll need to
use either a live version of the notebook with exhibitionist installed,
or fallback to static HTML repr()s.
- The server's socket isn't released until you call server.stop(), remember
to cleanup.
- Be aware that you are exposing your data through a local web server.
By default the server binds to localhost/127.0.0.1 which usually wouldn't
be accessible to other hosts on the network. In general, you should be
running in an environment where access is not a risk.
- Tornado is currently run with debug=False, because it's autoreload
feature can cause unexpected behaviour when files are modified while
working in IPython.
- Testing stale javascript/html due to the browser catch, gets you every time.
Disable caching for development, or do a hard refresh.

**I'm going to use this, what more should I know?**

- You can load views using just a prefix of the objid, just like
git let's you do. just use at least the first 8 characters, so:

so:
http://127.0.0.1:9083/myView/39c56ad2

is practically always interchangeable with:

http://127.0.0.1:9083/myView/39c56ad23ea1c2826a7406c9d8c42cc96884a406

- when calling server.add_handler() to register your handlers,
you can pass in a request handler class or a module/package,
Exhibitionist will look throgh them and discover all handler
classes decorated with @http_handler.

- `server.get_view_url` does some tricks for views with a route using
the special {{objid}} marker. You should read the docstring.

- see exhibitionist/providers/websocket/handlers for documentation
of the basic message format for the websocket channel.
You can also look at the frames going through the wire in
the "PingPong" example, with chrome developer tools support for
monitoring websocket connections.

- websocket clients that are both publisher and subscriber
on same channel, weill not receive messages they themselves publish.
on the python side, you can use the "exclude" parameter of server,notify_X()
to exclude a python callback from receiving it's own message.

- whatever extra keyword argument you pass to @http_handler
will be passed to the initialize(self,**kwds) method of
your request handler class, see tornado documentation
or test_server.py for an example.
