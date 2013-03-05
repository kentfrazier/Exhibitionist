#!/usr/bin/env python
import sys

print("\nINSTALLED VERSIONS")
print("------------------")
print("Python: %d.%d.%d.%s.%s" % sys.version_info[:])

try:
    import tornado
    print("tornado: %s" % tornado.version)
except:
    print("Tornado: Not installed")

try:
    import ws4py
    print("ws4py: %s" % ws4py.__version__)
except:
    print("ws4py: Not installed")

try:
    import requests
    print("Requests: %s" % requests.__version__)
except:
    print("Requests: Not installed")

print("\n")
