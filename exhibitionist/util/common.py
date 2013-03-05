# -*- coding: utf-8 -*-
from __future__ import print_function

class UrlDisplay(object):# pragma: no cover
    """Displays urls as text, hotlinks, or inline HTML if in IPython

    """
    def __init__(self, url, height="400px",width="100%"):
        self.url = url
        self.width = width
        self.height = height

    # noinspection PyBroadException
    @staticmethod
    def check_ipython():
        env = None
        try:
            ip = get_ipython()
            env = "ipython"

            # 0.13, 0.14/1.0dev keep the type of frontend in different places
            front_end = (ip.config.get('KernelApp') or
                         ip.config.get('IPKernelApp'))['parent_appname']
            if "qtconsole" in front_end:
                env = "qtconsole"
            elif "notebook" in front_end:
                env = "notebook"
        except:
            pass
        return env

    def notebook_repr(self):
        """ override this method"""

        tmpl = '<iframe src=%s style="width:100%%;height:%s; padding-bottom: 5px"></iframe>'
        result = tmpl % (self.url, self.height)
        return result

    def qtconsole_repr(self):
        """ override this method"""
        return 'Open this <a href="%s">link</a>  to View the object' % (self.url)

    def __repr__(self):
        return self.url

    def _repr_html_(self):

        if self.check_ipython() == 'notebook':
            return self.notebook_repr()
        elif self.check_ipython() == 'qtconsole':
            return self.qtconsole_repr()
        else:
            raise NotImplementedError()
