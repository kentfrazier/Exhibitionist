#!/bin/bash

echo "inside $0"

sudo apt-get install libevent-1.4-2 libevent-dev

# these are requirements for TESTING only
pip install -M nose
if [ ${TRAVIS_PYTHON_VERSION:0:1} == "2" ] ; then
    pip install -M gevent
    pip install -M grequests
fi

pip install -M requests
pip install -M coverage

# waiting on  https://github.com/Lawouach/WebSocket-for-Python/pull/81
# ws4py
pip install -v git+git://github.com/y-p/WebSocket-for-Python@7219233
