from __future__ import print_function

# Parts purloined from pandas and IPython's setup.py

from setuptools import setup, find_packages
import sys
import shutil
import os

if sys.version_info[:2] < (2,6):
    sys.stderr.write("Python >= 2.6 required")
    sys.exit(1)

PY3 = (sys.version_info[0] >= 3)

DISTNAME = 'pandas'
LICENSE = 'BSD'
AUTHOR = "Yoval P."
URL = "http://github.com/Exhibitionist/Exhibitionist"
DOWNLOAD_URL = ''
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
]

MAJOR = 0
MINOR = 1
MICRO = 0
ISRELEASED = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)
QUALIFIER = ''

FULLVERSION = VERSION

DESCRIPTION="Build a mini web-app to replace your object's repr() with an HTML+JS view"
LONG_DESCRIPTION="""
Exhibitionist is a Python library that let's you build tiny web-apps which serve as
views for live python objects in your favorite python shell.
It's built on top of [Tornado](http://www.tornadoweb.org/) and is easy to get started with, the "hello world"
example takes about 10 lines.

If you want to create fully interactive views of python objects using HTML and
leveraging javascript libraries such as [d3.js](http://d3js.org) or your favorite grid/charting
library, exhibitionist allows you to do that with very little boilerplate in a way that closely
follows modern web app development practices,
in both spirit and process.

The resulting views are available as urls served from a local server and are viewable directly in the browser.  Users of [IPython-notebook](http://gituhb.com/ipython/ipython ) can leverage it's inline display of HTML+Javascript for seamless integration of views into their interactive workflow.

*Features:*

- Out-of-the-box support for two-way message passing between javascript and python using a PubSub mechanism mechanism built on websockets.
- use AJAX to dynamically load data, work with large data sets, make things
interactive. do server things on the server and client things on the client.
- Designed to be a dependency of you library. import it and integrate HTML
views of you classes into your code. or monkey-patch an existing library
with your own UI. It's all good.
- Develop views with your favorite HTML/JS/CSS libraries. Everything is supported.
- Examples included as well as a heavily documented skeleton project to get you started.
- Supports Python 2.6+, 3.2+.
- Test-suite. Coverage. yep
- BSD-licensed, go crazy.
- Repo available on github:  [http://github.com/Exhibitionist/Exhibitionist](http://github.com/Exhibitionist/Exhibitionist)
"""
if not ISRELEASED:
    FULLVERSION += '.dev'
    try:
        import subprocess
        try:
            pipe = subprocess.Popen(["git", "rev-parse", "--short", "HEAD"],
                                    stdout=subprocess.PIPE).stdout
        except OSError:
            # msysgit compatibility
            pipe = subprocess.Popen(
                ["git.cmd", "rev-parse", "--short", "HEAD"],
                stdout=subprocess.PIPE).stdout
        rev = pipe.read().strip().decode('ascii')

        FULLVERSION += "-%s" % rev
    except:
        raise Exception("WARNING: Couldn't get git revision")
else:
    FULLVERSION += QUALIFIER

def cleanup():
    """Clean up the junk left around by the build process"""
    if "develop" not in sys.argv and "egg_info" not in sys.argv:
        try:
            shutil.rmtree('Exhibitionist.egg-info') # if it's a dir
            os.unlink('Exhibitionist.egg-info') # if it's a link
        except:
            pass


def write_version_py(filename=None):
    cnt = """\
version = '%s'
short_version = '%s'
"""
    if not filename:
        filename = os.path.join(
            os.path.dirname(__file__), 'exhibitionist', 'version.py')

    a = open(filename, 'w')
    try:
        a.write(cnt % (FULLVERSION, VERSION))
    finally:
        a.close()


setup_args=dict(
    name='Exhibitionist',
    version=VERSION,
    author='y-p',
    maintainer_email='Issues@at.github',
    packages = find_packages(exclude=['Examples']),
    url='http://www.github.com/y-p/Exhibitionist',
    license='LICENSE.txt',
    description=DESCRIPTION,
    tests_require=['nose',
                   'coverage',
                   'ws4py>=0.2.4', # for websockets
                   'requests', # for HTTP
                   #'gevent', # for parallel clients
                 ],
    test_suite='nose.collector',
    long_description=LONG_DESCRIPTION,
    install_requires = ['tornado>=2.4.1', 'six'],
    extras_require = dict(
        doc = 'Sphinx>=0.3',
        test = 'nose>=1.0',
    )
)

write_version_py() # generate exhibition/version.py

def main():
    setup(**setup_args)
    try:
        cleanup()
    except:
        pass

if __name__ == '__main__':
    main()
