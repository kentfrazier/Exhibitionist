#!/bin/bash

echo "inside $0"

# these are requirements for TESTING only
pip install -M nose
pip install -M requests
pip install -M grequests
pip install -M coverage

# waiting on  https://github.com/Lawouach/WebSocket-for-Python/pull/81
# ws4py
pip install -v git+git://github.com/y-p/WebSocket-for-Python@7219233
