#!/bin/bash

echo "inside $0"

pip install  tornado>=2.4.1, requests, six, nose,
# waiting on  https://github.com/Lawouach/WebSocket-for-Python/pull/81
# ws4py
pip install git+git://github.com/y-p/WebSocket-for-Python@7219233
